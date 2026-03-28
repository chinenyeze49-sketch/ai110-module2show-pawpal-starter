"""Automated test suite for PawPal+ system."""

from datetime import datetime, timedelta
import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_task(title="Test task", hour=9, priority=1, is_recurring=False):
    return Task(
        title=title,
        task_type="feeding",
        due_time=datetime.today().replace(hour=hour, minute=0, second=0, microsecond=0),
        priority=priority,
        is_recurring=is_recurring,
        recurrence_interval=timedelta(days=1) if is_recurring else None,
    )

def make_scheduler(*pets):
    owner = Owner(name="Test Owner", email="test@test.com", phone="000")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner=owner)


# ── Task tests ────────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """mark_complete() should set is_completed to True."""
    task = make_task()
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task count."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


# ── Sorting tests ─────────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return tasks earliest first."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    pet.add_task(make_task("Late task", hour=15))
    pet.add_task(make_task("Early task", hour=8))
    scheduler = make_scheduler(pet)
    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks[0].title == "Early task"
    assert sorted_tasks[1].title == "Late task"


def test_sort_by_priority_returns_highest_first():
    """sort_by_priority() should return priority 1 before priority 2."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    pet.add_task(make_task("Low priority", hour=8, priority=3))
    pet.add_task(make_task("High priority", hour=9, priority=1))
    scheduler = make_scheduler(pet)
    sorted_tasks = scheduler.sort_by_priority()
    assert sorted_tasks[0].title == "High priority"


# ── Recurrence tests ──────────────────────────────────────────────────────────

def test_recurring_task_generates_next_occurrence():
    """Completing a recurring task should generate one for the next day."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    task = make_task("Daily feeding", hour=8, is_recurring=True)
    pet.add_task(task)
    scheduler = make_scheduler(pet)
    task.mark_complete()
    new_tasks = scheduler.generate_recurring_tasks()
    assert len(new_tasks) == 1
    assert new_tasks[0].due_time.date() == (datetime.today() + timedelta(days=1)).date()


def test_non_recurring_task_does_not_generate_next():
    """A non-recurring completed task should not generate a new one."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    task = make_task("One-off task", hour=8, is_recurring=False)
    pet.add_task(task)
    scheduler = make_scheduler(pet)
    task.mark_complete()
    new_tasks = scheduler.generate_recurring_tasks()
    assert len(new_tasks) == 0


# ── Conflict detection tests ──────────────────────────────────────────────────

def test_detect_conflicts_flags_close_tasks():
    """Tasks within 30 minutes of each other should be flagged as conflicts."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    pet.add_task(make_task("Task A", hour=8))
    pet.add_task(make_task("Task B", hour=8))
    scheduler = make_scheduler(pet)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 2


def test_no_conflict_for_distant_tasks():
    """Tasks more than 30 minutes apart should not be flagged."""
    pet = Pet(name="Buddy", species="dog", breed="Lab", age=3)
    pet.add_task(make_task("Morning", hour=8))
    pet.add_task(make_task("Afternoon", hour=15))
    scheduler = make_scheduler(pet)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_scheduler_with_no_pets_returns_empty():
    """A scheduler with no pets should return empty lists."""
    scheduler = make_scheduler()
    assert scheduler.get_todays_tasks() == []
    assert scheduler.detect_conflicts() == []


def test_pet_with_no_tasks_returns_empty():
    """A pet with no tasks should return an empty list."""
    pet = Pet(name="Whiskers", species="cat", breed="Siamese", age=2)
    assert pet.get_tasks() == []

