"""PawPal+ - A pet care management system."""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Task:
    """Represents a single care task assigned to a pet."""

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

    def next_occurrence(self) -> Optional["Task"]:
        """If recurring, return a new Task for the next occurrence."""
        if not self.is_recurring or self.recurrence_interval is None:
            return None
        return Task(
            title=self.title,
            task_type=self.task_type,
            due_time=self.due_time + self.recurrence_interval,
            priority=self.priority,
            is_recurring=self.is_recurring,
            recurrence_interval=self.recurrence_interval,
        )


@dataclass
class Pet:
    """Represents a pet owned by an Owner."""

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
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet and clear its tasks."""
        if pet in self.pets:
            pet.tasks.clear()
            self.pets.remove(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Save owner, pets, and tasks to a JSON file."""
        data = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "breed": pet.breed,
                    "age": pet.age,
                    "tasks": [
                        {
                            "title": task.title,
                            "task_type": task.task_type,
                            "due_time": task.due_time.isoformat(),
                            "priority": task.priority,
                            "is_recurring": task.is_recurring,
                            "is_completed": task.is_completed,
                            "recurrence_interval_days": (
                                task.recurrence_interval.days
                                if task.recurrence_interval else None
                            ),
                        }
                        for task in pet.get_tasks()
                    ],
                }
                for pet in self.pets
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_from_json(filepath: str = "data.json") -> Optional["Owner"]:
        """Load owner, pets, and tasks from a JSON file. Returns None if file missing."""
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        owner = Owner(name=data["name"], email=data["email"], phone=data["phone"])
        for pet_data in data["pets"]:
            pet = Pet(
                name=pet_data["name"],
                species=pet_data["species"],
                breed=pet_data["breed"],
                age=pet_data["age"],
            )
            for task_data in pet_data["tasks"]:
                task = Task(
                    title=task_data["title"],
                    task_type=task_data["task_type"],
                    due_time=datetime.fromisoformat(task_data["due_time"]),
                    priority=task_data["priority"],
                    is_recurring=task_data["is_recurring"],
                    is_completed=task_data["is_completed"],
                    recurrence_interval=(
                        timedelta(days=task_data["recurrence_interval_days"])
                        if task_data["recurrence_interval_days"] else None
                    ),
                )
                pet.add_task(task)
            owner.add_pet(pet)
        return owner


class Scheduler:
    """Manages and organizes tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def _all_tasks(self) -> List[Task]:
        """Collect all tasks from every pet."""
        return [task for pet in self.owner.get_pets() for task in pet.get_tasks()]

    def get_todays_tasks(self) -> List[Task]:
        """Return all tasks due today."""
        return [t for t in self._all_tasks() if t.is_due_today()]

    def sort_by_priority(self) -> List[Task]:
        """Return today's tasks sorted by priority (1=highest) then time."""
        return sorted(self.get_todays_tasks(), key=lambda t: (t.priority, t.due_time))

    def sort_by_time(self) -> List[Task]:
        """Return today's tasks sorted by due time (earliest first)."""
        return sorted(self.get_todays_tasks(), key=lambda t: t.due_time)

    def filter_by_status(self, completed: bool = False) -> List[Task]:
        """Return today's tasks filtered by completion status."""
        return [t for t in self.get_todays_tasks() if t.is_completed == completed]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return today's tasks for a specific pet by name."""
        return [
            task
            for pet in self.owner.get_pets()
            if pet.name.lower() == pet_name.lower()
            for task in pet.get_tasks()
            if task.is_due_today()
        ]

    def generate_recurring_tasks(self) -> List[Task]:
        """For completed recurring tasks, create and add the next occurrence."""
        new_tasks = []
        for pet in self.owner.get_pets():
            for task in list(pet.get_tasks()):
                if task.is_completed and task.is_recurring:
                    next_task = task.next_occurrence()
                    if next_task:
                        pet.add_task(next_task)
                        new_tasks.append(next_task)
        return new_tasks

    def detect_conflicts(self) -> List[Task]:
        """Return tasks whose due times fall within 30 minutes of another task."""
        todays = self.sort_by_time()
        conflict_window = timedelta(minutes=30)
        conflicting: set = set()
        for i in range(len(todays)):
            for j in range(i + 1, len(todays)):
                if abs(todays[i].due_time - todays[j].due_time) < conflict_window:
                    conflicting.add(i)
                    conflicting.add(j)
        return [todays[i] for i in sorted(conflicting)]

    def find_next_available_slot(self, duration_minutes: int = 30) -> Optional[datetime]:
        """Find the next available time slot today with no tasks scheduled."""
        todays = self.sort_by_time()
        now = datetime.now().replace(second=0, microsecond=0)
        slot = now
        for task in todays:
            gap = (task.due_time - slot).total_seconds() / 60
            if gap >= duration_minutes:
                return slot
            slot = task.due_time + timedelta(minutes=duration_minutes)
        if slot.hour < 22:
            return slot
        return None