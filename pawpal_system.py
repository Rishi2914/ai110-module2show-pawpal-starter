from datetime import date as _date


def _time_to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def _minutes_to_time(total_minutes: int) -> str:
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


class Owner:
    def __init__(self, name: str, time_available_minutes: int, preferences: list[str]):
        self.name = name
        self.time_available_minutes = time_available_minutes
        self.preferences = preferences
        self.pets: list["Pet"] = []

    def add_pet(self, pet: "Pet") -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def set_time_available(self, minutes: int) -> None:
        """Update how many minutes the owner has available today."""
        self.time_available_minutes = minutes

    def get_pets(self) -> list["Pet"]:
        """Return all pets belonging to this owner."""
        return self.pets


class Pet:
    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list["PetCareTask"] = []

    def add_task(self, task: "PetCareTask") -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> list["PetCareTask"]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def clear_tasks(self) -> None:
        """Remove all tasks from this pet."""
        self.tasks = []


class PetCareTask:
    def __init__(self, title: str, duration_minutes: int, priority: str, category: str, is_recurring: bool, frequency: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_recurring = is_recurring
        self.frequency = frequency
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority.lower() == "high"

    def to_dict(self) -> dict:
        """Return a dictionary representation of this task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "is_recurring": self.is_recurring,
            "frequency": self.frequency,
        }


class Scheduler:
    def __init__(self, start_time: str, time_limit_minutes: int):
        self.start_time = start_time
        self.time_limit_minutes = time_limit_minutes

    def build_plan(self, pets: list["Pet"], owner: "Owner") -> "DailyPlan":
        """Build a daily schedule for all pets based on the owner's available time."""
        plan = DailyPlan(date=_date.today().isoformat())
        all_tasks = []
        for pet in pets:
            all_tasks.extend(pet.get_tasks())
        sorted_tasks = self.sort_tasks(all_tasks)
        current_time = _time_to_minutes(self.start_time)
        time_remaining = owner.time_available_minutes
        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                start = _minutes_to_time(current_time)
                end = _minutes_to_time(current_time + task.duration_minutes)
                plan.add_item(ScheduledItem(task, start, end, "fits within available time"))
                current_time += task.duration_minutes
                time_remaining -= task.duration_minutes
            else:
                plan.skip_task(task, "not enough time remaining")
        return plan

    def sort_tasks(self, tasks: list["PetCareTask"]) -> list["PetCareTask"]:
        """Sort tasks by priority (high first), then by duration shortest first."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: (priority_order.get(t.priority.lower(), 1), t.duration_minutes))

    def filter_tasks(self, tasks: list["PetCareTask"], time_remaining: int) -> list["PetCareTask"]:
        """Return only tasks whose duration fits within the remaining time."""
        return [t for t in tasks if t.duration_minutes <= time_remaining]

    def check_conflicts(self, items: list["ScheduledItem"]) -> bool:
        """Return True if any two scheduled items overlap in time."""
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if _time_to_minutes(a.start_time) < _time_to_minutes(b.end_time) and \
                   _time_to_minutes(b.start_time) < _time_to_minutes(a.end_time):
                    return True
        return False


class DailyPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_items: list["ScheduledItem"] = []
        self.total_duration_minutes: int = 0
        self.skipped_tasks: list[dict] = []

    def add_item(self, item: "ScheduledItem") -> None:
        """Add a scheduled item to the plan and update total duration."""
        self.scheduled_items.append(item)
        self.total_duration_minutes += item.duration()

    def skip_task(self, task: "PetCareTask", reason: str) -> None:
        """Record a task that could not be scheduled and why."""
        self.skipped_tasks.append({
            "title": task.title,
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "reason": reason,
        })

    def display(self) -> str:
        """Return a formatted timetable string of the day's schedule."""
        lines = [f"Daily Plan — {self.date}", "-" * 30]
        for item in self.scheduled_items:
            lines.append(f"{item.start_time} - {item.end_time}  {item.task.title}")
        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for t in self.skipped_tasks:
                lines.append(f"  {t['title']} ({t['reason']})")
        return "\n".join(lines)

    def explain(self) -> str:
        """Return a plain-text explanation of why each task was scheduled or skipped."""
        lines = [f"Plan explanation for {self.date}:"]
        for item in self.scheduled_items:
            lines.append(f"- {item.task.title} scheduled at {item.start_time}: {item.reason}")
        if self.skipped_tasks:
            lines.append("Not scheduled:")
            for t in self.skipped_tasks:
                lines.append(f"- {t['title']}: {t['reason']}")
        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Return a summary dict with counts and task lists for the plan."""
        return {
            "date": self.date,
            "total_duration_minutes": self.total_duration_minutes,
            "scheduled_count": len(self.scheduled_items),
            "skipped_count": len(self.skipped_tasks),
            "scheduled_tasks": [item.task.title for item in self.scheduled_items],
            "skipped_tasks": self.skipped_tasks,
        }


class ScheduledItem:
    def __init__(self, task: "PetCareTask", start_time: str, end_time: str, reason: str):
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason

    def duration(self) -> int:
        """Return the duration of this item in minutes."""
        return _time_to_minutes(self.end_time) - _time_to_minutes(self.start_time)

    def to_dict(self) -> dict:
        """Return a dictionary representation of this scheduled item."""
        return {
            "task": self.task.to_dict(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "reason": self.reason,
        }
