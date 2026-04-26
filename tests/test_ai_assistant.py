"""Tests for the AI assistant module — uses the deterministic mock provider
so tests are fast, offline, and reproducible (no API keys required)."""

from datetime import datetime, timedelta

from ai_assistant import (
    AIResponse,
    answer_care_question,
    check_safety,
    explain_plan,
    get_provider,
    score_confidence,
    suggest_tasks,
)
from pawpal_system import Owner, Pet, Scheduler, Task


# ── Helpers ────────────────────────────────────────────────────────────────

def _scheduler_with_two_tasks():
    owner = Owner(name="Test", email="t@t.com", phone="000")
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    pet.add_task(Task(
        title="Feed",
        task_type="feeding",
        due_time=datetime.today().replace(hour=8, minute=0,
                                          second=0, microsecond=0),
        priority=1,
    ))
    pet.add_task(Task(
        title="Walk",
        task_type="walk",
        due_time=datetime.today().replace(hour=15, minute=0,
                                          second=0, microsecond=0),
        priority=2,
    ))
    owner.add_pet(pet)
    return Scheduler(owner=owner)


# ── Provider selection ─────────────────────────────────────────────────────

def test_get_provider_defaults_to_mock(monkeypatch):
    monkeypatch.delenv("PAWPAL_AI_PROVIDER", raising=False)
    assert get_provider().name == "mock"


def test_get_provider_explicit_mock():
    assert get_provider("mock").name == "mock"


# ── Safety guardrails ──────────────────────────────────────────────────────

def test_check_safety_blocks_dosage_question():
    assert check_safety("What dosage of ibuprofen is safe?") == "vet_redirect"


def test_check_safety_blocks_emergency_keyword():
    assert check_safety("My dog ate chocolate, help!") == "vet_redirect"


def test_check_safety_allows_normal_question():
    assert check_safety("How often should I walk my dog?") is None


def test_answer_care_question_redirects_unsafe_input():
    resp = answer_care_question("What dosage of tylenol can I give my cat?")
    assert resp.guardrail == "vet_redirect"
    assert "vet" in resp.text.lower()


def test_answer_care_question_validates_empty_input():
    resp = answer_care_question("   ")
    assert resp.source == "validation"
    assert resp.confidence < 0.5


# ── Confidence scoring ────────────────────────────────────────────────────

def test_score_confidence_low_for_short_text():
    assert score_confidence("ok", "mock", None) < 0.5


def test_score_confidence_higher_for_real_provider():
    text = "Most adult dogs need 30-60 minutes of walking per day; consult your vet."
    mock_score = score_confidence(text, "mock", None)
    real_score = score_confidence(text, "anthropic", None)
    assert real_score > mock_score


def test_score_confidence_guardrail_high():
    assert score_confidence("redirect text", "guardrail", "vet_redirect") >= 0.9


# ── Feature: explain_plan ─────────────────────────────────────────────────

def test_explain_plan_returns_aiResponse():
    scheduler = _scheduler_with_two_tasks()
    resp = explain_plan(scheduler)
    assert isinstance(resp, AIResponse)
    assert resp.source == "mock"
    assert len(resp.text) > 20
    assert 0.0 <= resp.confidence <= 1.0


def test_explain_plan_handles_empty_schedule():
    """Empty schedule shouldn't crash — should return a sensible message."""
    owner = Owner(name="T", email="t@t.com", phone="000")
    scheduler = Scheduler(owner=owner)
    resp = explain_plan(scheduler)
    assert resp.text  # non-empty
    assert resp.source == "mock"


# ── Feature: suggest_tasks ────────────────────────────────────────────────

def test_suggest_tasks_dog_returns_dog_specific():
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=2)
    resp = suggest_tasks(pet)
    assert resp.source == "mock"
    # Mock should mention "walk" for a dog.
    assert "walk" in resp.text.lower()


def test_suggest_tasks_cat_returns_cat_specific():
    pet = Pet(name="Whiskers", species="cat", breed="Siamese", age=4)
    resp = suggest_tasks(pet)
    # Mock should mention "litter" for a cat.
    assert "litter" in resp.text.lower()


# ── Feature: answer_care_question ─────────────────────────────────────────

def test_answer_care_question_normal_input_returns_text():
    resp = answer_care_question("How often should I walk my dog?")
    assert resp.source == "mock"
    assert len(resp.text) > 20
    assert resp.guardrail is None


def test_answer_care_question_logs_confidence_in_range():
    resp = answer_care_question("How much food does a Lab need?")
    assert 0.0 < resp.confidence <= 1.0


# ── Error handling ────────────────────────────────────────────────────────

class _FailingProvider:
    """Simulates a provider whose API call raises."""
    name = "failing"

    def complete(self, system, user):
        raise RuntimeError("network down")


def test_explain_plan_falls_back_on_provider_error():
    scheduler = _scheduler_with_two_tasks()
    resp = explain_plan(scheduler, provider=_FailingProvider())
    assert resp.source == "error_fallback"
    assert resp.confidence < 0.5


def test_answer_care_question_falls_back_on_provider_error():
    resp = answer_care_question("How often should I walk?",
                                provider=_FailingProvider())
    assert resp.source == "error_fallback"


def test_suggest_tasks_falls_back_on_provider_error():
    pet = Pet(name="Test", species="dog", breed="Mix", age=1)
    resp = suggest_tasks(pet, provider=_FailingProvider())
    assert resp.source == "error_fallback"
