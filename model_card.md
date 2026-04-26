# PawPal+ — Model Card & Reflection

This file is the rubric's required `model_card.md`. It documents what the system is, what it isn't, and what I learned while building it. The four bolded reflection questions below come straight from the spec.

---

## 1. What is the system?

**PawPal+** is a Python + Streamlit pet-care planner. It has:

- A deterministic domain layer (`pawpal_system.py`) that models `Owner`, `Pet`, `Task`, and a `Scheduler` that sorts, filters, detects conflicts, and finds free slots.
- An AI layer (`ai_assistant.py`) that adds three LLM-powered features on top of the domain:
  1. **Explain the plan** — natural-language explanation of why today's schedule is ordered the way it is.
  2. **Suggest tasks** — a starter task list for a newly added pet, tailored to species/breed/age. (This is the "agent-y" feature: it acts on the user's behalf to pre-fill structure.)
  3. **Care Q&A** — open-ended pet-care questions, with a regex guardrail that intercepts dosage/diagnosis/emergency questions and redirects to a vet.

The AI provider is pluggable: `mock` (default, deterministic, for offline demos and tests), `anthropic`, or `openai`.

## 2. What is it for?

A busy pet owner using it as a daily planning aid — adding tasks, generating today's schedule, getting a sanity-check explanation of the plan, and asking general care questions.

## 3. What it is **not** for

- Veterinary advice. Dosage, diagnosis, poisoning, and emergency questions are blocked by the guardrail.
- Authoritative breed-specific care plans. The model offers general best practices; owners should verify with a vet.
- Multi-user / production use. There's no auth, no database, and `data.json` is a single-user store.

---

## 4. Required reflection answers

> _The four questions in this section come directly from the rubric's "Reflection and Ethics" section._

### 4.1 What are the limitations or biases in your system?

- **English-only.** Both the regex guardrail and the prompts assume English input.
- **Western-pet bias.** The mock provider's hard-coded suggestions assume cats, dogs, and rabbits as the common species — exotic pets get a generic fallback.
- **Heuristic confidence.** The confidence score is a hand-rolled heuristic, not a calibrated probability. Two responses with the same score aren't necessarily equally trustworthy.
- **Conflict window is global.** The scheduler treats two tasks within 30 minutes as conflicting even if they belong to different pets one owner could handle simultaneously. I noted this tradeoff is intentional but it would mislead a power user with a large household.
- **No persistence of AI history.** Plan explanations and Q&A answers are not saved, so the user can't review yesterday's reasoning.

### 4.2 Could it be misused, and how have you mitigated that?

| Misuse | Mitigation |
|---|---|
| **Substituting the assistant for a vet.** Someone could paste "my cat ate xylitol" and act on the answer. | Hard-coded regex guardrail blocks every dosage / poisoning / emergency / diagnosis pattern *before* the prompt is sent. The redirect message tells the user to call a vet or pet poison helpline. |
| **Acting on hallucinated breed-specific advice.** | The system prompt instructs the model to hedge, prefer general rules, and recommend consulting a vet for variation. The confidence heuristic *increases* when hedging language ("consult", "depends on", "general rule") is present, so the UI rewards calibrated answers. |
| **Logging sensitive owner data.** | Logs only record category, provider, confidence — not the full question text. Pet names appear at debug level only. |
| **Provider downtime breaking the demo.** | Every AI call is wrapped in try/except with a low-confidence canned fallback. The mock provider is the default so a network outage never breaks the eval or the test suite. |

### 4.3 What surprised you while testing your AI?

- The **regex guardrail catches more than I expected**. I started with a small pattern list and "my dog ate chocolate, help!" still matched on `\bate (?:chocolate|...|)\b`. That one rule saved me from realizing later that emergency triage was a separate intent class.
- **Hedging language correlates with accuracy.** I added the "+0.1 if the response contains words like 'consult' or 'depends on'" rule on a hunch, then noticed that the eval items where the mock cited "consult your vet" were the ones I felt most comfortable shipping. It's a weak signal but a real one.
- **The mock provider is more useful than I thought.** I added it for tests, but I now develop with `PAWPAL_AI_PROVIDER=mock` because feedback is instant. Real-LLM calls go in for evaluation runs and the demo recording. Splitting "develop" from "demo" providers wasn't a planned design move — it emerged.

### 4.4 Describe one helpful and one flawed AI suggestion

**Helpful — splitting the AI layer from the domain.**
While drafting, I asked the assistant whether the AI features should live as methods on `Scheduler`. It pushed back: keep `Scheduler` deterministic and put AI in a separate module, so tests don't need an API key and so swapping providers doesn't ripple through scheduling code. I took that suggestion exactly. The current two-layer split (`pawpal_system.py` ↔ `ai_assistant.py`) is the single most important design decision in the project, and it came from the AI.

**Flawed — over-engineering the confidence score.**
The first draft of `score_confidence()` came back with a calibrated logistic regression over five features and a unit-test suite that asserted exact float values. That was wrong: the rubric asks for *a* confidence signal, the values are heuristic anyway, and the precise floats made the tests brittle (they would break the moment I tweaked a coefficient). I rejected it and rewrote `score_confidence()` as a transparent additive heuristic — a starting score plus small bumps for length, real provider, and hedging language. Tests now assert relative ordering ("real provider > mock") instead of exact floats, which is what actually matters. The lesson: when the answer is "any reasonable signal," a simple, defensible heuristic beats a precise-looking model.

---

## 5. How I tested it

| Layer | How |
|---|---|
| Domain logic | `tests/test_pawpal.py` (10 tests) — sorting, recurrence, conflicts, edge cases |
| Input validation | `tests/test_validation.py` (7 tests) — bad priority, empty names, etc. |
| AI features | `tests/test_ai_assistant.py` (19 tests) — provider selection, guardrails, all three features, confidence scoring, error fallback |
| End-to-end behavior | `eval/run_eval.py` — a 10-item held-out set producing per-category accuracy + average confidence summary stats |

Run all of it: `python -m pytest tests/ -v && python eval/run_eval.py`.

---

## 6. Confidence I'm shipping

- **Scheduler logic:** high. Pure Python, fully tested, no surprise behavior.
- **Guardrails:** high for the patterns covered; low for adversarial paraphrases. A model-based intent classifier would be the obvious next step but feels like over-build for this milestone.
- **Generated AI text quality:** medium. The mock is plausible. The real Anthropic provider produces noticeably better explanations but introduces non-determinism — that's why the eval is rule-based, not exact-match.
