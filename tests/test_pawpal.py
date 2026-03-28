"""Quick tests for PawPal+ core logic."""

from datetime import datetime, timedelta
from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """Verify that mark_complete() sets is_completed to True."""
    task = Task(
        title="Feed Buddy",
        task_type="feeding",
        due_time=datetime.today(),
        priority=1,
    )
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_count():
    """Verify that adding a task to a Pet increases its task count."""
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
    task = Task(
        title="Walk",
        task_type="walk",
        due_time=datetime.today(),
        priority=2,
    )
    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1

