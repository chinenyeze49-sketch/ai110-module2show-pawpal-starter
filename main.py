"""PawPal+ demo script — prints today's schedule to the terminal."""

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

# Create owner
owner = Owner(name="Alex Rivera", email="alex@example.com", phone="555-0100")

# Create two pets
buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="cat", breed="Siamese", age=5)
owner.add_pet(buddy)
owner.add_pet(whiskers)

# Add tasks (all due today)
today = datetime.today()

buddy.add_task(Task(
    title="Morning feeding",
    task_type="feeding",
    due_time=today.replace(hour=8, minute=0),
    priority=1,
    is_recurring=True,
    recurrence_interval=timedelta(days=1),
))
buddy.add_task(Task(
    title="Afternoon walk",
    task_type="walk",
    due_time=today.replace(hour=15, minute=0),
    priority=2,
))
whiskers.add_task(Task(
    title="Medication",
    task_type="medication",
    due_time=today.replace(hour=8, minute=20),
    priority=1,
))

# Schedule
scheduler = Scheduler(owner=owner)

print("=== Today's Schedule ===")
for task in scheduler.sort_by_priority():
    status = "✓" if task.is_completed else "○"
    print(f"[{status}] {task.due_time.strftime('%H:%M')} | Priority {task.priority} | {task.title}")

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\n⚠ Conflicts detected:")
    for task in conflicts:
        print(f"  - {task.title} @ {task.due_time.strftime('%H:%M')}")
else:
    print("\nNo conflicts detected.")


