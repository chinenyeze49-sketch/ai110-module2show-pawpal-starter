"""PawPal+ demo CLI — exercises the deterministic scheduler AND the AI features.

This is the script used in the Loom walkthrough. It deliberately runs through
three end-to-end inputs so the rubric checklist (end-to-end run / AI feature /
reliability or evaluation behavior) is all visible in one demo:

    python main.py
"""

from datetime import datetime, timedelta

from tabulate import tabulate

from ai_assistant import answer_care_question, explain_plan, suggest_tasks
from logging_config import configure_logging
from pawpal_system import Owner, Pet, Scheduler, Task

configure_logging()

# ── Build a small world ─────────────────────────────────────────────────────
owner = Owner(name="Alex Rivera", email="alex@example.com", phone="555-0100")
buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="cat", breed="Siamese", age=5)
owner.add_pet(buddy)
owner.add_pet(whiskers)

today = datetime.today()

buddy.add_task(Task(
    title="Afternoon walk",
    task_type="walk",
    due_time=today.replace(hour=15, minute=0),
    priority=2,
))
buddy.add_task(Task(
    title="Morning feeding",
    task_type="feeding",
    due_time=today.replace(hour=8, minute=0),
    priority=1,
    is_recurring=True,
    recurrence_interval=timedelta(days=1),
))
whiskers.add_task(Task(
    title="Medication",
    task_type="medication",
    due_time=today.replace(hour=8, minute=20),
    priority=1,
))
whiskers.add_task(Task(
    title="Vet appointment",
    task_type="appointment",
    due_time=today.replace(hour=8, minute=40),
    priority=1,
))

scheduler = Scheduler(owner=owner)


def priority_label(p):
    return {1: "🔴 High", 2: "🟡 Medium"}.get(p, "🟢 Low")


def task_icon(t):
    return {"feeding": "🍖", "walk": "🦮",
            "medication": "💊", "appointment": "🏥"}.get(t, "📌")


# ── 1. Show the deterministic schedule ──────────────────────────────────────
print("\n╔══════════════════════════════╗")
print("║      🐾 PawPal+ Schedule      ║")
print("╚══════════════════════════════╝\n")

rows = [
    [
        task_icon(t.task_type),
        t.due_time.strftime("%H:%M"),
        priority_label(t.priority),
        t.title,
        t.task_type,
        "✓ Done" if t.is_completed else "○ Pending",
    ]
    for t in scheduler.sort_by_time()
]
print(tabulate(rows, headers=["", "Time", "Priority", "Task", "Type", "Status"],
               tablefmt="rounded_outline"))

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\n⚠  CONFLICTS DETECTED:")
    print(tabulate([[t.title, t.due_time.strftime("%H:%M")] for t in conflicts],
                   headers=["Task", "Time"], tablefmt="rounded_outline"))
else:
    print("\n✅ No scheduling conflicts.")

slot = scheduler.find_next_available_slot()
print(f"\n📅 Next available slot: {slot.strftime('%H:%M')}" if slot
      else "\n📅 No available slots today.")

# ── 2. AI feature 1: explain the plan ───────────────────────────────────────
print("\n──────── 🤖 AI: Plan Explanation ────────")
plan_resp = explain_plan(scheduler)
print(plan_resp.text)
print(f"[provider={plan_resp.source}  confidence={plan_resp.confidence:.2f}]")

# ── 3. AI feature 2: suggest tasks for a new pet ────────────────────────────
print("\n──────── 🤖 AI: Task Suggestions for Whiskers ────────")
sugg = suggest_tasks(whiskers)
print(sugg.text)
print(f"[provider={sugg.source}  confidence={sugg.confidence:.2f}]")

# ── 4. AI feature 3: care Q&A with guardrail demo ───────────────────────────
print("\n──────── 🤖 AI: Care Q&A ────────")
q1 = "How often should I bathe my Siamese cat?"
print(f"Q: {q1}")
print(answer_care_question(q1).text)

print()
q2 = "What dosage of ibuprofen is safe for my dog?"
print(f"Q: {q2}")
guarded = answer_care_question(q2)
print(guarded.text)
print(f"[guardrail={guarded.guardrail}  confidence={guarded.confidence:.2f}]")
