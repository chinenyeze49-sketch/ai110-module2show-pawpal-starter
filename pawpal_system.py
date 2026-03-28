"""PawPal+ - A pet care management system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Task:
    """Represents a single care task assigned to a pet (e.g. feeding, vet visit)."""

    title: str
    task_type: str
    due_time: datetime
    priority: int
    is_recurring: bool = False
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def is_due_today(self) -> bool:
        """Return True if this task is due today."""
        pass


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
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        pass


class Owner:
    """Represents a pet owner who manages one or more pets."""

    def __init__(self, name: str, email: str, phone: str) -> None:
        self.name: str = name
        self.email: str = email
        self.phone: str = phone
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list of pets."""
        pass

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        pass


class Scheduler:
    """Manages and organizes tasks across all pets for scheduling and conflict detection."""

    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler."""
        pass

    def get_todays_tasks(self) -> List[Task]:
        """Return all tasks due today."""
        pass

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted from highest to lowest priority."""
        pass

    def detect_conflicts(self) -> List[Task]:
        """Return tasks that overlap in due time, indicating a scheduling conflict."""
        pass
