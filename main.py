"""PawPal+ demo script — professional CLI output with tabulate."""

from datetime import datetime, timedelta
from tabulate import tabulate
from pawpal_system import Task, Pet, Owner, Scheduler

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
    return {"feeding": "🍖", "walk": "🦮", "medication": "💊", "appointment": "🏥"}.get(t, "📌")

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

print(tabulate(
    rows,
    headers=["", "Time", "Priority", "Task", "Type", "Status"],
    tablefmt="rounded_outline"
))

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\n⚠  CONFLICTS DETECTED:")
    conflict_rows = [[t.title, t.due_time.strftime("%H:%M")] for t in conflicts]
    print(tabulate(conflict_rows, headers=["Task", "Time"], tablefmt="rounded_outline"))
else:
    print("\n✅ No scheduling conflicts.")

slot = scheduler.find_next_available_slot()
if slot:
    print(f"\n📅 Next available slot: {slot.strftime('%H:%M')}")
else:
    print("\n📅 No available slots today.")
