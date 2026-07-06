from __future__ import annotations
from datetime import date as _date, timedelta as _timedelta

_BREAK_INTERVAL_MINUTES = 60
_BREAK_DURATION_MINUTES = 5
_FREQUENCY_DAYS: dict[str, int] = {"daily": 1, "weekly": 7}


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
        """Add a pet to this owner's pet list, ignoring duplicates by name."""
        if any(p.name == pet.name for p in self.pets):
            return
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
        """Add a care task, silently ignoring duplicates by title."""
        if any(t.title == task.title for t in self.tasks):
            return
        self.tasks.append(task)

    def complete_task(self, title: str) -> "PetCareTask | None":
        """Mark the named task complete and, if recurring, replace it with a fresh instance.

        Returns the new next-occurrence task for recurring tasks, None for one-off tasks.
        Silently does nothing if the title is not found or is already completed.
        """
        for task in self.tasks:
            if task.title == title and not task.completed:
                next_task = task.mark_complete()
                # retire the completed instance; slot in the fresh one if recurring
                self.tasks = [t for t in self.tasks if t is not task]
                if next_task:
                    self.tasks.append(next_task)
                return next_task
        return None

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
    def __init__(self, title: str, duration_minutes: int, priority: str, category: str, is_recurring: bool, frequency: str, due_date: _date | None = None):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_recurring = is_recurring
        self.frequency = frequency
        self.completed = False
        self.due_date = due_date  # None means no due date assigned yet

    def mark_complete(self) -> "PetCareTask | None":
        """Mark this task as completed and return a fresh next occurrence for recurring tasks.

        The next occurrence's due_date is set to today + the interval defined by frequency:
          daily  → today + timedelta(days=1)
          weekly → today + timedelta(days=7)
        Returns None for non-recurring tasks.
        """
        self.completed = True
        days = _FREQUENCY_DAYS.get(self.frequency)
        if self.is_recurring and days is not None:
            next_due = _date.today() + _timedelta(days=days)
            return PetCareTask(
                self.title, self.duration_minutes, self.priority,
                self.category, self.is_recurring, self.frequency,
                due_date=next_due,
            )
        return None

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
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }


class Scheduler:
    def __init__(self, start_time: str, time_limit_minutes: int):
        self.start_time = start_time
        self.time_limit_minutes = time_limit_minutes

    def build_plan(self, pets: list["Pet"], owner: "Owner") -> "DailyPlan":
        """Build a daily schedule for all pets based on the owner's available time."""
        plan = DailyPlan(date=_date.today().isoformat())
        task_pet: dict[int, str] = {}
        all_tasks = []
        for pet in pets:
            for task in pet.get_tasks():
                if not task.completed:  # skip already-completed tasks
                    all_tasks.append(task)
                    task_pet[id(task)] = pet.name

        sorted_tasks = self.sort_tasks(all_tasks, owner.preferences, task_pet)
        current_time = _time_to_minutes(self.start_time)
        time_remaining = min(owner.time_available_minutes, self.time_limit_minutes)
        time_since_break = 0
        scheduled_ids: set[int] = set()

        for task in sorted_tasks:
            pet_name = task_pet[id(task)]
            if task.duration_minutes <= time_remaining:
                # insert a break after every _BREAK_INTERVAL_MINUTES of scheduled work,
                # but only when there is room for both the break and the next task
                if (time_since_break >= _BREAK_INTERVAL_MINUTES
                        and time_remaining >= _BREAK_DURATION_MINUTES + task.duration_minutes):
                    current_time += _BREAK_DURATION_MINUTES
                    time_remaining -= _BREAK_DURATION_MINUTES
                    time_since_break = 0
                    plan.breaks_inserted += 1

                reason = "high-priority, scheduled first" if task.is_high_priority() else "fits within available time"
                start = _minutes_to_time(current_time)
                end = _minutes_to_time(current_time + task.duration_minutes)
                plan.add_item(ScheduledItem(task, start, end, reason, pet_name))
                current_time += task.duration_minutes
                time_remaining -= task.duration_minutes
                time_since_break += task.duration_minutes
                scheduled_ids.add(id(task))
            # no else/break — keep scanning for smaller tasks that still fit

        # record skips after the full pass so smaller lower-priority tasks get a chance first
        for task in sorted_tasks:
            if id(task) not in scheduled_ids:
                pet_name = task_pet[id(task)]
                skip_reason = (
                    "high-priority task skipped — extend available time to include it"
                    if task.is_high_priority()
                    else "not enough time remaining"
                )
                plan.skip_task(task, skip_reason, pet_name)

        for a, b in self.find_conflicts(plan.scheduled_items):
            plan.add_conflict(a, b)
        return plan

    def sort_tasks(self, tasks: list["PetCareTask"], preferences: list[str] = None, task_pet: dict = None) -> list["PetCareTask"]:
        """Sort by priority (high first), preferred categories, pet name (grouping), then shortest duration."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        preferred = set(preferences or [])
        pet_map = task_pet or {}
        return sorted(tasks, key=lambda t: (
            priority_order.get(t.priority.lower(), 1),
            0 if t.category in preferred else 1,
            pet_map.get(id(t), ""),   # group same-priority tasks by pet to reduce context-switching
            t.duration_minutes,
        ))

    def sort_by_time(self, tasks: list["PetCareTask"], reverse: bool = False) -> list["PetCareTask"]:
        """Return a new list of tasks sorted solely by duration_minutes.

        Sorting shortest-first (the default) is useful for filling a tight time budget
        with as many tasks as possible. Longest-first is useful for identifying the most
        time-intensive tasks at a glance or for scheduling anchor tasks early.

        Args:
            tasks:   Any list of PetCareTask objects — does not have to come from a pet
                     or plan; flat lists assembled by the caller work fine.
            reverse: False (default) → shortest first. True → longest first.

        Returns:
            A new sorted list; the original list is not modified.
        """
        return sorted(tasks, key=lambda t: t.duration_minutes, reverse=reverse)

    def filter_tasks(self, tasks: list["PetCareTask"], time_remaining: int) -> list["PetCareTask"]:
        """Return only tasks whose duration fits within the remaining time."""
        return [t for t in tasks if t.duration_minutes <= time_remaining]

    def filter_tasks_by(
        self,
        tasks: list["PetCareTask"],
        task_pet: dict[int, str] = None,
        *,
        completed: bool = None,
        pet_name: str = None,
    ) -> list["PetCareTask"]:
        """Return tasks that match all supplied filter criteria (AND logic).

        Both filters are optional. Omitting one skips that dimension entirely, so
        calling with no keyword arguments returns the original list unchanged.

        Args:
            tasks:      Source list of PetCareTask objects to filter.
            task_pet:   Mapping of {id(task): pet_name} used to resolve ownership.
                        Only required when pet_name is supplied; ignored otherwise.
                        Build it with: {id(t): p.name for p in pets for t in p.get_tasks()}
            completed:  True  → keep only tasks where task.completed is True.
                        False → keep only tasks where task.completed is False.
                        None  → do not filter by completion status (default).
            pet_name:   When provided, keep only tasks whose id maps to this pet name
                        inside task_pet. Tasks absent from task_pet are excluded.

        Returns:
            A new list containing only tasks that satisfy every active filter.
            Returns an empty list (not None) when nothing matches.
        """
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            mapping = task_pet or {}
            result = [t for t in result if mapping.get(id(t)) == pet_name]
        return result

    def find_conflicts(self, items: list["ScheduledItem"]) -> list[tuple["ScheduledItem", "ScheduledItem"]]:
        """Return every pair of ScheduledItems whose time windows overlap.

        Uses the standard interval-overlap test: two intervals [s1, e1) and [s2, e2)
        overlap when s1 < e2 AND s2 < e1. Touching endpoints (e.g. 08:00–08:30 and
        08:30–09:00) are treated as adjacent, not overlapping.

        Checks all unique pairs in O(n²) — acceptable for typical daily task counts
        (< 20 items). Both same-pet and cross-pet overlaps are reported.

        Args:
            items: List of ScheduledItem objects to check. Order does not matter.

        Returns:
            List of (a, b) tuples for each overlapping pair, in the order they were
            found. Returns an empty list when the schedule is conflict-free.
        """
        pairs = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if (_time_to_minutes(a.start_time) < _time_to_minutes(b.end_time) and
                        _time_to_minutes(b.start_time) < _time_to_minutes(a.end_time)):
                    pairs.append((a, b))
        return pairs

    def check_conflicts(self, items: list["ScheduledItem"]) -> bool:
        """Return True if any two scheduled items overlap in time, False otherwise.

        Convenience wrapper around find_conflicts for use in boolean guards (e.g.
        assertions, early-exit checks) when the specific conflicting pairs are not
        needed. Stops as soon as the first conflict is found via find_conflicts.

        Args:
            items: List of ScheduledItem objects to check.

        Returns:
            True if at least one overlapping pair exists; False if the schedule is clean.
        """
        return bool(self.find_conflicts(items))

    def warn_conflicts(self, items: list["ScheduledItem"]) -> str | None:
        """Return a formatted warning string when overlaps exist, or None when the schedule is clean.

        Lightweight alternative to find_conflicts for display-only use cases — the
        caller receives a single ready-to-print string rather than a list of tuples
        to unpack. Returns None (instead of an empty string) so callers can use a
        simple truthiness check: `if msg := scheduler.warn_conflicts(items): print(msg)`.

        Args:
            items: List of ScheduledItem objects to check.

        Returns:
            A multi-line string starting with a conflict count summary, followed by
            one line per conflicting pair. Returns None if no conflicts are found.
        """
        pairs = self.find_conflicts(items)
        if not pairs:
            return None
        lines = [f"Warning: {len(pairs)} scheduling conflict(s) detected:"]
        for a, b in pairs:
            lines.append(
                f"  [{a.pet_name}] {a.task.title} ({a.start_time}–{a.end_time})"
                f" overlaps [{b.pet_name}] {b.task.title} ({b.start_time}–{b.end_time})"
            )
        return "\n".join(lines)


class DailyPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_items: list["ScheduledItem"] = []
        self.total_duration_minutes: int = 0
        self.skipped_tasks: list[dict] = []
        self.breaks_inserted: int = 0
        self.conflicts: list[dict] = []

    def add_item(self, item: "ScheduledItem") -> None:
        """Add a scheduled item to the plan and update total duration."""
        self.scheduled_items.append(item)
        self.total_duration_minutes += item.duration()

    def skip_task(self, task: "PetCareTask", reason: str, pet_name: str = "") -> None:
        """Record a task that could not be scheduled and why."""
        self.skipped_tasks.append({
            "pet": pet_name,
            "title": task.title,
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "reason": reason,
        })

    def add_conflict(self, a: "ScheduledItem", b: "ScheduledItem") -> None:
        """Record an overlapping pair in this plan's conflict log.

        Stores both items as a flat dict so downstream consumers (display, explain,
        get_summary, app.py) can render the conflict without holding ScheduledItem
        references. Called by Scheduler.build_plan for each pair returned by
        find_conflicts.

        Args:
            a: The first conflicting ScheduledItem.
            b: The second conflicting ScheduledItem.
        """
        self.conflicts.append({
            "pet_a": a.pet_name, "task_a": a.task.title,
            "start_a": a.start_time, "end_a": a.end_time,
            "pet_b": b.pet_name, "task_b": b.task.title,
            "start_b": b.start_time, "end_b": b.end_time,
        })

    def display(self) -> str:
        """Return a formatted timetable string of the day's schedule."""
        lines = [f"Daily Plan — {self.date}", "-" * 30]
        for item in self.scheduled_items:
            lines.append(f"{item.start_time} - {item.end_time}  [{item.pet_name}] {item.task.title}")
        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for t in self.skipped_tasks:
                lines.append(f"  [{t['pet']}] {t['title']} ({t['reason']})")
        if self.conflicts:
            lines.append("\n⚠ Conflicts detected:")
            for c in self.conflicts:
                lines.append(
                    f"  [{c['pet_a']}] {c['task_a']} ({c['start_a']}–{c['end_a']})"
                    f" overlaps [{c['pet_b']}] {c['task_b']} ({c['start_b']}–{c['end_b']})"
                )
        return "\n".join(lines)

    def explain(self) -> str:
        """Return a plain-text explanation of why each task was scheduled or skipped."""
        lines = [f"Plan explanation for {self.date}:"]
        if self.breaks_inserted:
            lines.append(
                f"  ({self.breaks_inserted} × {_BREAK_DURATION_MINUTES}-min break inserted "
                f"after each {_BREAK_INTERVAL_MINUTES} min of scheduled work)"
            )
        for item in self.scheduled_items:
            lines.append(f"- [{item.pet_name}] {item.task.title} scheduled at {item.start_time}: {item.reason}")
        if self.skipped_tasks:
            lines.append("Not scheduled:")
            for t in self.skipped_tasks:
                lines.append(f"- [{t['pet']}] {t['title']}: {t['reason']}")
        if self.conflicts:
            lines.append(f"Conflicts ({len(self.conflicts)}):")
            for c in self.conflicts:
                lines.append(
                    f"- [{c['pet_a']}] {c['task_a']} ({c['start_a']}–{c['end_a']})"
                    f" overlaps [{c['pet_b']}] {c['task_b']} ({c['start_b']}–{c['end_b']})"
                )
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
            "breaks_inserted": self.breaks_inserted,
            "conflicts": self.conflicts,
        }


class ScheduledItem:
    def __init__(self, task: "PetCareTask", start_time: str, end_time: str, reason: str, pet_name: str = ""):
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason
        self.pet_name = pet_name

    def duration(self) -> int:
        """Return the duration of this item in minutes."""
        return _time_to_minutes(self.end_time) - _time_to_minutes(self.start_time)

    def to_dict(self) -> dict:
        """Return a dictionary representation of this scheduled item."""
        return {
            "pet_name": self.pet_name,
            "task": self.task.to_dict(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "reason": self.reason,
        }
