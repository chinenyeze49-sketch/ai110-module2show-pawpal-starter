"""Tests for the input-validation guards added to the domain classes."""

from datetime import datetime, timedelta

import pytest

from pawpal_system import Owner, Pet, Task


def test_task_rejects_empty_title():
    with pytest.raises(ValueError):
        Task(title="  ", task_type="feeding",
             due_time=datetime.today(), priority=1)


def test_task_rejects_priority_out_of_range():
    with pytest.raises(ValueError):
        Task(title="x", task_type="feeding",
             due_time=datetime.today(), priority=0)
    with pytest.raises(ValueError):
        Task(title="x", task_type="feeding",
             due_time=datetime.today(), priority=6)


def test_task_recurring_requires_interval():
    with pytest.raises(ValueError):
        Task(title="x", task_type="feeding",
             due_time=datetime.today(), priority=1,
             is_recurring=True)


def test_task_recurring_with_interval_ok():
    task = Task(title="x", task_type="feeding",
                due_time=datetime.today(), priority=1,
                is_recurring=True,
                recurrence_interval=timedelta(days=1))
    assert task.is_recurring is True


def test_pet_rejects_empty_name():
    with pytest.raises(ValueError):
        Pet(name="", species="dog", breed="Lab", age=1)


def test_pet_rejects_negative_age():
    with pytest.raises(ValueError):
        Pet(name="Buddy", species="dog", breed="Lab", age=-1)


def test_owner_rejects_empty_name():
    with pytest.raises(ValueError):
        Owner(name="", email="t@t.com", phone="000")
