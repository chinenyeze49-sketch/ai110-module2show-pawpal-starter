"""PawPal+ evaluation harness.

Loads eval/eval_set.json, runs each item against the AI features, and
produces a summary accuracy stat per category and overall.

Usage:
    python eval/run_eval.py                    # uses mock provider (offline)
    PAWPAL_AI_PROVIDER=anthropic python eval/run_eval.py   # uses real LLM

Designed so the same script works with any provider — checks are
deterministic rules over the AIResponse (category, guardrail, length,
keyword presence) rather than exact-match, since LLMs vary.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

# Make project root importable when run directly.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ai_assistant import answer_care_question, suggest_tasks  # noqa: E402
from logging_config import configure_logging  # noqa: E402
from pawpal_system import Pet  # noqa: E402

configure_logging()


def _check(item: dict) -> tuple[bool, str, dict]:
    """Run one eval item. Returns (passed, note, response_dict)."""
    cat = item["category"]
    expected = item["expected"]

    if cat in ("guardrail", "care_qa", "validation"):
        resp = answer_care_question(item["input"])
        if "guardrail" in expected:
            ok = resp.guardrail == expected["guardrail"]
            return ok, f"guardrail={resp.guardrail!r}", asdict(resp)
        if "source" in expected:
            ok = resp.source == expected["source"]
            return ok, f"source={resp.source!r}", asdict(resp)
        if "min_length" in expected:
            ok = (resp.guardrail is None
                  and len(resp.text) >= expected["min_length"])
            return ok, f"len={len(resp.text)}", asdict(resp)
        return False, "no rule matched", asdict(resp)

    if cat == "suggest":
        pet = Pet(**item["input_pet"])
        resp = suggest_tasks(pet)
        keywords = expected["contains_any"]
        text_lower = resp.text.lower()
        ok = any(k in text_lower for k in keywords)
        return ok, f"keywords_seen={[k for k in keywords if k in text_lower]}", asdict(resp)

    return False, f"unknown category {cat}", {}


def main():
    eval_path = ROOT / "eval" / "eval_set.json"
    with open(eval_path) as f:
        spec = json.load(f)

    results = []
    by_cat: dict = {}

    for item in spec["items"]:
        passed, note, resp = _check(item)
        results.append({
            "id": item["id"],
            "category": item["category"],
            "passed": passed,
            "note": note,
            "confidence": resp.get("confidence"),
            "source": resp.get("source"),
        })
        by_cat.setdefault(item["category"], []).append(passed)

    # ── Summary stats (the rubric explicitly asks for at least one) ────────
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    overall_acc = passed / total if total else 0.0
    confidences = [r["confidence"] for r in results if r["confidence"] is not None]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    print("\nPawPal+ evaluation results")
    print("=" * 60)
    print(f"Provider: {os.environ.get('PAWPAL_AI_PROVIDER', 'mock')}")
    print(f"Total items: {total}")
    print(f"Passed: {passed}")
    print(f"Overall accuracy: {overall_acc:.0%}")
    print(f"Average confidence: {avg_conf:.2f}")
    print()
    print("Per-category accuracy:")
    for cat, vals in sorted(by_cat.items()):
        acc = sum(vals) / len(vals)
        print(f"  {cat:<12} {acc:.0%}  ({sum(vals)}/{len(vals)})")
    print()
    print("Per-item:")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        conf = r["confidence"] if r["confidence"] is not None else 0.0
        print(f"  {mark} [{r['category']:<10}] {r['id']:<15} "
              f"conf={conf:.2f} {r['note']}")

    # Write machine-readable report
    out = ROOT / "eval" / "last_run.json"
    with open(out, "w") as f:
        json.dump({
            "provider": os.environ.get("PAWPAL_AI_PROVIDER", "mock"),
            "overall_accuracy": overall_acc,
            "average_confidence": avg_conf,
            "by_category": {k: sum(v) / len(v) for k, v in by_cat.items()},
            "items": results,
        }, f, indent=2)
    print(f"\nWrote {out}")

    # Non-zero exit if anything failed (handy for CI later).
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
