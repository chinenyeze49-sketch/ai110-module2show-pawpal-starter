"""PawPal+ demo script — tests sorting, filtering, recurring tasks, conflicts."""

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

owner = Owner(name="Alex Rivera", email="alex@example.com", phone="555-0100")

buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="cat", breed="Siamese", age=5)
owner.add_pet(buddy)
owner.add_pet(whiskers)

today = datetime.today()

# Add tasks out of order to test sorting
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
# Conflict task — within 30 mins of medication
whiskers.add_task(Task(
    title="Vet appointment",
    task_type="appointment",
    due_time=today.replace(hour=8, minute=40),
    priority=1,
))

scheduler = Scheduler(owner=owner)

print("=== Sorted by Time ===")
for t in scheduler.sort_by_time():
    print(f"  {t.due_time.strftime('%H:%M')} | {t.title}")

print("\n=== Sorted by Priority ===")
for t in scheduler.sort_by_priority():
    print(f"  [{t.priority}] {t.title}")

print("\n=== Pending Tasks Only ===")
for t in scheduler.filter_by_status(completed=False):
    print(f"  {t.title}")

print("\n=== Buddy's Tasks ===")
for t in scheduler.filter_by_pet("Buddy"):
    print(f"  {t.title}")

print("\n=== Conflicts ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for t in conflicts:
        print(f"  ⚠ {t.title} @ {t.due_time.strftime('%H:%M')}")
else:
    print("  No conflicts.")

print("\n=== Recurring Task Generation ===")
# Mark morning feeding complete and generate next occurrence
for pet in owner.get_pets():
    for task in pet.get_tasks():
        if task.title == "Morning feeding":
            task.mark_complete()

new_tasks = scheduler.generate_recurring_tasks()
print(f"  Generated {len(new_tasks)} new recurring task(s):")
for t in new_tasks:
    print(f"  → {t.title} due {t.due_time.strftime('%Y-%m-%d %H:%M')}")
