"""PawPal+ AI assistant — adds language-model features on top of the deterministic scheduler.

Provides three AI features:
  1. explain_plan(scheduler)   -> plain-English explanation of why a generated daily
                                  plan is ordered the way it is.
  2. suggest_tasks(pet)        -> a starter list of care tasks tailored to a pet's
                                  species/breed/age (the agent feature).
  3. answer_care_question(q)   -> open-ended pet-care Q&A with safety guardrails.

The module supports three providers (selected via PAWPAL_AI_PROVIDER env var):
  - "anthropic"  -> real Claude API call (requires ANTHROPIC_API_KEY)
  - "openai"     -> real OpenAI API call (requires OPENAI_API_KEY)
  - "mock"       -> deterministic fake responses, used for tests and offline demos
                    so the system always has a reproducible fallback.

Every public function returns an AIResponse with:
  - text:        the model's response
  - confidence:  float 0-1, simple heuristic score
  - source:      provider name
  - guardrail:   short reason if a safety guardrail rewrote/blocked the response
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from pawpal_system import Pet, Scheduler, Task

logger = logging.getLogger("pawpal.ai")


# ────────────────────────────────────────────────────────────────────────────
# Response shape
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class AIResponse:
    """Wraps every AI feature's output with metadata used for logging + UI."""
    text: str
    confidence: float
    source: str
    guardrail: Optional[str] = None
    inputs_summary: str = ""
    citations: List[str] = field(default_factory=list)


# ────────────────────────────────────────────────────────────────────────────
# Safety guardrails
# ────────────────────────────────────────────────────────────────────────────

# These patterns trigger a "redirect to vet" response. PawPal+ is a planning
# tool, not a medical authority, so any prompt that asks for diagnosis,
# dosage, or emergency advice is rewritten into a safe answer.
_VET_REDIRECT_PATTERNS = [
    r"\bdosage\b",
    r"\bhow much (?:medicine|medication|tylenol|ibuprofen|aspirin)\b",
    r"\bdiagnos(?:e|is)\b",
    r"\bemergenc(?:y|ies)\b",
    r"\bbleeding\b",
    r"\bpoison(?:ed|ing)?\b",
    r"\bseizure\b",
    r"\bcan'?t breathe\b",
    r"\bate (?:chocolate|grapes|onion|xylitol)\b",
]


def check_safety(question: str) -> Optional[str]:
    """Return a guardrail reason string if `question` should be redirected, else None."""
    q = question.lower()
    for pattern in _VET_REDIRECT_PATTERNS:
        if re.search(pattern, q):
            return "vet_redirect"
    return None


_VET_REDIRECT_MESSAGE = (
    "I'm a planning assistant, not a veterinarian. Questions about dosages, "
    "diagnoses, poisoning, or emergencies should go straight to your vet or "
    "a 24/7 pet poison helpline. Please don't rely on me for medical advice."
)


# ────────────────────────────────────────────────────────────────────────────
# Provider abstraction
# ────────────────────────────────────────────────────────────────────────────

class _MockProvider:
    """Deterministic fake LLM. Generates plausible responses based on prompt
    keywords so tests run offline and the demo always works without an API key."""

    name = "mock"

    def complete(self, system: str, user: str) -> str:
        u = user.lower()
        if "explain this daily plan" in u or "explain the plan" in u:
            return self._mock_plan_explanation(user)
        if "suggest a starter set" in u or "suggest care tasks" in u:
            return self._mock_task_suggestions(user)
        # Generic care Q&A
        return self._mock_care_answer(user)

    def _mock_plan_explanation(self, user: str) -> str:
        # Pull task lines out of the prompt for a plausible echo
        lines = [ln.strip("- ").strip() for ln in user.splitlines()
                 if ln.strip().startswith("- ")]
        if not lines:
            return "The plan is empty — there are no tasks scheduled for today."
        first = lines[0]
        return (
            f"This plan front-loads the highest-priority items so nothing time-"
            f"sensitive slips. {first} comes first because it's marked priority "
            f"1 — usually medication or a vet appointment. Lower-priority "
            f"enrichment and grooming tasks fall later in the day so the morning "
            f"stays calm. Items within 30 minutes of each other are flagged so "
            f"you can rearrange before they cause a real conflict."
        )

    def _mock_task_suggestions(self, user: str) -> str:
        species = "dog"
        for s in ("cat", "rabbit", "bird", "dog"):
            if s in user.lower():
                species = s
                break
        if species == "dog":
            return (
                "1. Morning feeding — 7:30am, priority 1, recurring daily\n"
                "2. Morning walk — 8:00am, priority 2, recurring daily\n"
                "3. Midday training (5 mins) — 12:30pm, priority 3\n"
                "4. Evening feeding — 6:00pm, priority 1, recurring daily\n"
                "5. Evening walk — 7:00pm, priority 2, recurring daily"
            )
        if species == "cat":
            return (
                "1. Morning feeding — 7:30am, priority 1, recurring daily\n"
                "2. Litter box scoop — 8:00am, priority 2, recurring daily\n"
                "3. Play session (10 mins) — 6:00pm, priority 3, recurring daily\n"
                "4. Evening feeding — 6:30pm, priority 1, recurring daily\n"
                "5. Brushing — 8:00pm, priority 4, twice a week"
            )
        return (
            "1. Morning feeding — 8:00am, priority 1, recurring daily\n"
            "2. Cage/enclosure check — 8:15am, priority 2, recurring daily\n"
            "3. Enrichment time — 5:00pm, priority 3, recurring daily\n"
            "4. Evening feeding — 6:00pm, priority 1, recurring daily"
        )

    def _mock_care_answer(self, user: str) -> str:
        if "bath" in user.lower():
            return ("For most cats, brushing is enough — they groom themselves and "
                    "rarely need baths unless they get into something. Check with "
                    "your vet for breed-specific advice.")
        if "walk" in user.lower():
            return ("Most adult dogs need at least 30–60 minutes of walking per day, "
                    "split into morning and evening. Adjust based on breed energy "
                    "level and age.")
        if "feed" in user.lower() or "food" in user.lower():
            return ("Adult dogs typically eat twice a day; cats often prefer smaller, "
                    "more frequent meals. Always check the food packaging for "
                    "weight-based portion guidance.")
        return ("That's a great care question — the general rule is to prioritize "
                "consistency in feeding and exercise, and to consult your vet for "
                "anything that varies from your pet's normal routine.")


class _AnthropicProvider:
    name = "anthropic"

    def __init__(self) -> None:
        try:
            import anthropic  # noqa: F401  (lazy import, only on real calls)
        except ImportError as e:
            raise RuntimeError(
                "anthropic package not installed. Run: pip install anthropic"
            ) from e
        self._anthropic = __import__("anthropic")

    def complete(self, system: str, user: str) -> str:
        client = self._anthropic.Anthropic()
        msg = client.messages.create(
            model=os.environ.get("PAWPAL_AI_MODEL", "claude-haiku-4-5-20251001"),
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        # Concatenate text blocks
        return "".join(getattr(b, "text", "") for b in msg.content)


class _OpenAIProvider:
    name = "openai"

    def __init__(self) -> None:
        try:
            import openai  # noqa: F401
        except ImportError as e:
            raise RuntimeError(
                "openai package not installed. Run: pip install openai"
            ) from e
        self._openai = __import__("openai")

    def complete(self, system: str, user: str) -> str:
        client = self._openai.OpenAI()
        resp = client.chat.completions.create(
            model=os.environ.get("PAWPAL_AI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=600,
        )
        return resp.choices[0].message.content or ""


def get_provider(name: Optional[str] = None):
    """Pick a provider by name or env var. Defaults to mock for offline reliability."""
    name = (name or os.environ.get("PAWPAL_AI_PROVIDER") or "mock").lower()
    if name == "anthropic":
        return _AnthropicProvider()
    if name == "openai":
        return _OpenAIProvider()
    return _MockProvider()


# ────────────────────────────────────────────────────────────────────────────
# Confidence scoring
# ────────────────────────────────────────────────────────────────────────────

def score_confidence(text: str, source: str, guardrail: Optional[str]) -> float:
    """Heuristic confidence score in [0, 1].

    Idea: confidence is higher when the system has more anchoring signal
    (longer response, real-provider answer, no guardrail rewrite). It's a
    deliberately simple heuristic — the rubric asks for *some* confidence
    signal, not a calibrated probability. A future iteration could replace
    this with a self-evaluation prompt.
    """
    if guardrail == "vet_redirect":
        # We deliberately refused — high confidence in the refusal itself.
        return 0.95
    if not text or len(text.strip()) < 20:
        return 0.2
    score = 0.5
    if source == "anthropic" or source == "openai":
        score += 0.2
    if len(text.split()) > 60:
        score += 0.1
    if any(marker in text.lower() for marker in (
        "consult", "vet", "depends on", "check with", "general rule"
    )):
        # Hedging language is good — model isn't overclaiming.
        score += 0.1
    return min(score, 0.95)


# ────────────────────────────────────────────────────────────────────────────
# Public AI features
# ────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = (
    "You are PawPal+, a friendly assistant that helps pet owners plan daily "
    "care. Keep answers concise (under 120 words), practical, and grounded in "
    "general pet-care best practices. Never give veterinary diagnoses, "
    "medication dosages, or emergency advice — redirect those questions to a "
    "vet. Prefer suggestions a busy owner can actually act on today."
)


def _format_plan(scheduler: Scheduler) -> str:
    tasks = scheduler.sort_by_priority()
    if not tasks:
        return "(no tasks scheduled today)"
    return "\n".join(
        f"- {t.due_time.strftime('%H:%M')} priority {t.priority} — "
        f"{t.title} ({t.task_type})"
        for t in tasks
    )


def explain_plan(scheduler: Scheduler, provider=None) -> AIResponse:
    """Generate a natural-language explanation of today's schedule."""
    provider = provider or get_provider()
    plan_text = _format_plan(scheduler)

    user_prompt = (
        "Explain this daily plan in plain English to the owner. Mention which "
        "task comes first and why, and call out anything that might cause a "
        "scheduling conflict.\n\n"
        f"PLAN:\n{plan_text}"
    )

    try:
        text = provider.complete(_SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        logger.exception("explain_plan failed: %s", e)
        return AIResponse(
            text=("Couldn't reach the AI provider — falling back to the raw "
                  "schedule. The first task is the highest priority of the day."),
            confidence=0.3,
            source="error_fallback",
            inputs_summary=plan_text,
        )

    response = AIResponse(
        text=text.strip(),
        confidence=score_confidence(text, provider.name, None),
        source=provider.name,
        inputs_summary=plan_text,
    )
    logger.info(
        "explain_plan ok provider=%s tasks=%d conf=%.2f",
        provider.name, len(scheduler.get_todays_tasks()), response.confidence,
    )
    return response


def suggest_tasks(pet: Pet, provider=None) -> AIResponse:
    """Suggest a starter task list for a pet (acts as a small care-planner agent)."""
    provider = provider or get_provider()

    user_prompt = (
        f"Suggest a starter set of 4–6 daily care tasks for this pet, formatted "
        f"as a numbered list with time-of-day, priority (1=highest, 5=lowest), "
        f"and whether the task should recur daily.\n\n"
        f"PET:\n- name: {pet.name}\n- species: {pet.species}\n"
        f"- breed: {pet.breed}\n- age: {pet.age} years"
    )

    try:
        text = provider.complete(_SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        logger.exception("suggest_tasks failed: %s", e)
        return AIResponse(
            text=("Couldn't reach the AI provider — defaulting to feeding x2 "
                  "and exercise x1 as a safe baseline."),
            confidence=0.3,
            source="error_fallback",
            inputs_summary=f"{pet.species} {pet.breed} age {pet.age}",
        )

    response = AIResponse(
        text=text.strip(),
        confidence=score_confidence(text, provider.name, None),
        source=provider.name,
        inputs_summary=f"{pet.species} {pet.breed} age {pet.age}",
    )
    logger.info(
        "suggest_tasks ok provider=%s species=%s conf=%.2f",
        provider.name, pet.species, response.confidence,
    )
    return response


def answer_care_question(question: str, provider=None) -> AIResponse:
    """Answer an open-ended pet-care question, with vet-redirect guardrails."""
    provider = provider or get_provider()

    guardrail = check_safety(question)
    if guardrail == "vet_redirect":
        logger.warning("answer_care_question blocked by guardrail: %s", question[:80])
        return AIResponse(
            text=_VET_REDIRECT_MESSAGE,
            confidence=score_confidence(_VET_REDIRECT_MESSAGE, "guardrail", guardrail),
            source="guardrail",
            guardrail=guardrail,
            inputs_summary=question[:120],
        )

    if not question or not question.strip():
        return AIResponse(
            text="Please type a question about pet care so I can help.",
            confidence=0.2,
            source="validation",
            inputs_summary="",
        )

    user_prompt = f"Pet-care question from the owner: {question.strip()}"
    try:
        text = provider.complete(_SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        logger.exception("answer_care_question failed: %s", e)
        return AIResponse(
            text=("Couldn't reach the AI provider right now. Try again in a "
                  "moment, or check with your vet for anything urgent."),
            confidence=0.3,
            source="error_fallback",
            inputs_summary=question[:120],
        )

    response = AIResponse(
        text=text.strip(),
        confidence=score_confidence(text, provider.name, None),
        source=provider.name,
        inputs_summary=question[:120],
    )
    logger.info(
        "answer_care_question ok provider=%s conf=%.2f",
        provider.name, response.confidence,
    )
    return response


__all__ = [
    "AIResponse",
    "answer_care_question",
    "check_safety",
    "explain_plan",
    "get_provider",
    "score_confidence",
    "suggest_tasks",
]
