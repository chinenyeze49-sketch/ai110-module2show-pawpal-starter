"""PawPal+ - A pet care management system."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    """Represents a single care task assigned to a pet (e.g. feeding, vet visit)."""

    title: str
    task_type: str
    due_time: datetime
    priority: int
    is_recurring: bool = False
    is_completed: bool = False
    recurrence_interval: Optional[timedelta] = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def is_due_today(self) -> bool:
        """Return True if this task is due today."""
        return self.due_time.date() == datetime.today().date()


@dataclass
class Pet:
    """Represents a pet owned by an Owner, along with its associated care tasks."""

    name: str
    species: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


class Owner:
    """Represents a pet owner who manages one or more pets."""

    def __init__(self, name: str, email: str, phone: str) -> None:
        self.name: str = name
        self.email: str = email
        self.phone: str = phone
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet and clear its tasks, then remove it from the owner's list."""
        if pet in self.pets:
            pet.tasks.clear()
            self.pets.remove(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets


class Scheduler:
    """Manages and organizes tasks across all pets for scheduling and conflict detection."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner

    def _all_tasks(self) -> List[Task]:
        """Collect all tasks from every pet belonging to the owner."""
        return [task for pet in self.owner.get_pets() for task in pet.get_tasks()]

    def get_todays_tasks(self) -> List[Task]:
        """Return all tasks due today."""
        return [task for task in self._all_tasks() if task.is_due_today()]

    def sort_by_priority(self) -> List[Task]:
        """Return today's tasks sorted by priority (1 = highest)."""
        return sorted(self.get_todays_tasks(), key=lambda t: t.priority)

    def detect_conflicts(self) -> List[Task]:
        """Return tasks whose due times fall within 30 minutes of another task."""
        todays = self.sort_by_priority()
        conflict_window = timedelta(minutes=30)
        conflicting: set[int] = set()

        for i in range(len(todays)):
            for j in range(i + 1, len(todays)):
                delta = abs(todays[i].due_time - todays[j].due_time)
                if delta < conflict_window:
                    conflicting.add(i)
                    conflicting.add(j)

        return [todays[i] for i in sorted(conflicting)]
