from datetime import date, timedelta

import pytest

from pawpal_system import DailyPlan, Owner, Pet, PetCareTask, ScheduledItem, Scheduler


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def scheduler():
    return Scheduler(start_time="08:00", time_limit_minutes=120)


@pytest.fixture
def owner():
    return Owner(name="Alex", time_available_minutes=90, preferences=[])


def make_task(title="Walk", duration=20, priority="high", category="exercise",
              recurring=True, frequency="daily"):
    return PetCareTask(title, duration, priority, category, recurring, frequency)


def make_item(title, start, end, pet="Buddy", duration=None, priority="high"):
    task = make_task(title=title, priority=priority,
                     duration=duration or _minutes(end) - _minutes(start))
    return ScheduledItem(task, start, end, "test", pet)


def _minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m


# ── Happy paths ───────────────────────────────────────────────────────────────

class TestBuildPlanHappyPath:
    def test_all_tasks_scheduled_when_time_is_sufficient(self, scheduler, owner):
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk",    30, "high"))
        dog.add_task(make_task("Feeding", 10, "high"))
        owner.add_pet(dog)

        summary = scheduler.build_plan(owner.get_pets(), owner).get_summary()

        assert summary["scheduled_count"] == 2
        assert summary["skipped_count"] == 0

    def test_high_priority_scheduled_before_low(self, scheduler, owner):
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Playtime", 15, "low"))
        dog.add_task(make_task("Feeding",  10, "high"))
        owner.add_pet(dog)

        items = scheduler.build_plan(owner.get_pets(), owner).scheduled_items
        titles = [i.task.title for i in items]

        assert titles.index("Feeding") < titles.index("Playtime")

    def test_preferred_category_scheduled_before_non_preferred(self, scheduler):
        owner = Owner("Alex", 90, preferences=["nutrition"])
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Bath",    15, "medium", "grooming"))
        dog.add_task(make_task("Feeding", 10, "medium", "nutrition"))
        owner.add_pet(dog)

        items = scheduler.build_plan(owner.get_pets(), owner).scheduled_items
        titles = [i.task.title for i in items]

        assert titles.index("Feeding") < titles.index("Bath")


class TestRecurringTasksHappyPath:
    def test_daily_task_due_date_is_tomorrow(self):
        next_task = make_task(frequency="daily").mark_complete()

        assert next_task is not None
        assert next_task.due_date == date.today() + timedelta(days=1)

    def test_weekly_task_due_date_is_seven_days_out(self):
        next_task = make_task(frequency="weekly").mark_complete()

        assert next_task is not None
        assert next_task.due_date == date.today() + timedelta(days=7)

    def test_next_occurrence_starts_incomplete(self):
        next_task = make_task(frequency="daily").mark_complete()

        assert next_task.completed is False

    def test_pet_complete_task_replaces_instance_in_list(self):
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk", recurring=True, frequency="daily"))
        dog.complete_task("Walk")

        tasks = dog.get_tasks()
        assert len(tasks) == 1
        assert tasks[0].completed is False


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEmptyAndZeroInputs:
    def test_pet_with_no_tasks_produces_empty_schedule(self, scheduler, owner):
        owner.add_pet(Pet("Buddy", "Dog", 3))
        summary = scheduler.build_plan(owner.get_pets(), owner).get_summary()

        assert summary["scheduled_count"] == 0
        assert summary["skipped_count"] == 0

    def test_owner_with_zero_minutes_skips_all_tasks(self, scheduler):
        owner = Owner("Alex", time_available_minutes=0, preferences=[])
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk", 30))
        owner.add_pet(dog)
        summary = scheduler.build_plan(owner.get_pets(), owner).get_summary()

        assert summary["scheduled_count"] == 0
        assert summary["skipped_count"] == 1

    def test_sort_by_time_on_empty_list_returns_empty(self, scheduler):
        assert scheduler.sort_by_time([]) == []

    def test_filter_tasks_by_on_empty_list_returns_empty(self, scheduler):
        assert scheduler.filter_tasks_by([]) == []


class TestBoundaryConditions:
    def test_task_duration_exactly_equal_to_time_remaining_is_scheduled(self, scheduler):
        owner = Owner("Alex", time_available_minutes=30, preferences=[])
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk", duration=30))
        owner.add_pet(dog)
        summary = scheduler.build_plan(owner.get_pets(), owner).get_summary()

        assert summary["scheduled_count"] == 1
        assert summary["skipped_count"] == 0

    def test_high_priority_task_skipped_when_only_low_priority_fits(self, scheduler):
        owner = Owner("Alex", time_available_minutes=10, preferences=[])
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk",    30, "high"))   # too long
        dog.add_task(make_task("Feeding",  5, "low"))    # fits
        owner.add_pet(dog)
        plan = scheduler.build_plan(owner.get_pets(), owner)
        scheduled_titles = [i.task.title for i in plan.scheduled_items]
        skipped_titles   = [t["title"]   for t in plan.skipped_tasks]

        assert "Feeding" in scheduled_titles
        assert "Walk" in skipped_titles
        assert "extend available time" in plan.skipped_tasks[0]["reason"]


class TestConflictDetection:
    def test_touching_endpoints_are_not_flagged_as_conflict(self, scheduler):
        a = make_item("Walk",    "08:00", "08:30")
        b = make_item("Feeding", "08:30", "08:45")

        assert scheduler.find_conflicts([a, b]) == []
        assert scheduler.warn_conflicts([a, b]) is None

    def test_same_start_time_is_a_conflict(self, scheduler):
        a = make_item("Walk",    "08:00", "08:30")
        b = make_item("Feeding", "08:00", "08:15")

        assert len(scheduler.find_conflicts([a, b])) == 1

    def test_partial_overlap_is_a_conflict(self, scheduler):
        a = make_item("Walk",    "08:00", "08:30")
        b = make_item("Feeding", "08:15", "08:45")

        assert len(scheduler.find_conflicts([a, b])) == 1

    def test_cross_pet_overlap_is_detected(self, scheduler):
        a = make_item("Walk",    "08:00", "08:30", pet="Buddy")
        b = make_item("Feeding", "08:00", "08:10", pet="Mochi")

        assert len(scheduler.find_conflicts([a, b])) == 1

    def test_warn_conflicts_returns_string_when_conflict_exists(self, scheduler):
        a = make_item("Walk",    "08:00", "08:30")
        b = make_item("Feeding", "08:00", "08:15")
        result = scheduler.warn_conflicts([a, b])

        assert isinstance(result, str)
        assert "Warning" in result


class TestRecurringEdgeCases:
    def test_non_recurring_mark_complete_returns_none(self):
        task = make_task(recurring=False)

        assert task.mark_complete() is None

    def test_completing_already_completed_task_is_noop(self):
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk"))
        dog.get_tasks()[0].completed = True  # mark done without triggering replace logic

        result = dog.complete_task("Walk")

        assert result is None

    def test_completing_nonexistent_title_returns_none(self):
        dog = Pet("Buddy", "Dog", 3)

        assert dog.complete_task("Ghost Task") is None

    def test_completed_task_excluded_from_build_plan(self, scheduler, owner):
        dog = Pet("Buddy", "Dog", 3)
        task = make_task("Walk", duration=30)
        task.mark_complete()
        dog.tasks.append(task)   # insert already-completed task directly
        owner.add_pet(dog)
        summary = scheduler.build_plan(owner.get_pets(), owner).get_summary()

        assert summary["scheduled_count"] == 0


class TestDuplicateGuards:
    def test_duplicate_task_title_is_ignored(self):
        dog = Pet("Buddy", "Dog", 3)
        dog.add_task(make_task("Walk"))
        dog.add_task(make_task("Walk"))

        assert len(dog.get_tasks()) == 1

    def test_duplicate_pet_name_is_ignored(self, owner):
        owner.add_pet(Pet("Buddy", "Dog", 3))
        owner.add_pet(Pet("Buddy", "Dog", 5))

        assert len(owner.get_pets()) == 1


class TestFiltering:
    def test_filter_completed_false_excludes_done_tasks(self, scheduler):
        done = make_task("Walk")
        done.mark_complete()
        pending = make_task("Bath", recurring=False)

        result = scheduler.filter_tasks_by([done, pending], completed=False)

        assert result == [pending]

    def test_filter_completed_true_with_no_done_tasks_returns_empty(self, scheduler):
        tasks = [make_task("Walk")]

        assert scheduler.filter_tasks_by(tasks, completed=True) == []

    def test_filter_by_pet_name_returns_only_that_pets_tasks(self, scheduler):
        dog = Pet("Buddy", "Dog", 3)
        cat = Pet("Mochi", "Cat", 5)
        dog.add_task(make_task("Walk"))
        cat.add_task(make_task("Feeding"))
        all_tasks = [t for p in [dog, cat] for t in p.get_tasks()]
        task_pet  = {id(t): p.name for p in [dog, cat] for t in p.get_tasks()}

        result = scheduler.filter_tasks_by(all_tasks, task_pet, pet_name="Buddy")

        assert len(result) == 1
        assert task_pet[id(result[0])] == "Buddy"

    def test_filter_with_no_kwargs_returns_original_list(self, scheduler):
        tasks = [make_task("Walk"), make_task("Bath", recurring=False)]

        assert scheduler.filter_tasks_by(tasks) == tasks
