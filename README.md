# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
========================================
       TODAY'S SCHEDULE
========================================
Daily Plan — 2026-07-02
------------------------------
08:00 - 08:10  Feeding
08:10 - 08:25  Feeding
08:25 - 08:55  Morning Walk
08:55 - 09:05  Litter Box Clean
09:05 - 09:25  Bath Time

Skipped:
  Playtime (not enough time remaining)

Plan explanation for 2026-07-02:
- Feeding scheduled at 08:00: fits within available time
- Feeding scheduled at 08:10: fits within available time
- Morning Walk scheduled at 08:25: fits within available time
- Litter Box Clean scheduled at 08:55: fits within available time
- Bath Time scheduled at 09:05: fits within available time
Not scheduled:
- Playtime: not enough time remaining

Total time used: 85 min
Tasks scheduled: 5
Tasks skipped:   1

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/ -v

# Run with coverage:
python -m pytest tests/ --cov
```

The test suite covers 28 cases across 8 areas: scheduling happy paths (priority order, preferred categories, all tasks fit), recurring task due dates (daily +1 day, weekly +7 days), empty and zero-input edge cases, boundary conditions (exact time fit, high-priority task skipped when only a lower-priority one fits), conflict detection (overlapping vs touching endpoints, cross-pet), duplicate guards, and filtering by completion status or pet name.

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Library/Developer/CommandLineTools/usr/bin/python3
cachedir: .pytest_cache
rootdir: /Users/thiru/Documents/pawpal+
collecting ... collected 28 items

tests/test_pawpal.py::TestBuildPlanHappyPath::test_all_tasks_scheduled_when_time_is_sufficient PASSED [  3%]
tests/test_pawpal.py::TestBuildPlanHappyPath::test_high_priority_scheduled_before_low PASSED [  7%]
tests/test_pawpal.py::TestBuildPlanHappyPath::test_preferred_category_scheduled_before_non_preferred PASSED [ 10%]
tests/test_pawpal.py::TestRecurringTasksHappyPath::test_daily_task_due_date_is_tomorrow PASSED [ 14%]
tests/test_pawpal.py::TestRecurringTasksHappyPath::test_weekly_task_due_date_is_seven_days_out PASSED [ 17%]
tests/test_pawpal.py::TestRecurringTasksHappyPath::test_next_occurrence_starts_incomplete PASSED [ 21%]
tests/test_pawpal.py::TestRecurringTasksHappyPath::test_pet_complete_task_replaces_instance_in_list PASSED [ 25%]
tests/test_pawpal.py::TestEmptyAndZeroInputs::test_pet_with_no_tasks_produces_empty_schedule PASSED [ 28%]
tests/test_pawpal.py::TestEmptyAndZeroInputs::test_owner_with_zero_minutes_skips_all_tasks PASSED [ 32%]
tests/test_pawpal.py::TestEmptyAndZeroInputs::test_sort_by_time_on_empty_list_returns_empty PASSED [ 35%]
tests/test_pawpal.py::TestEmptyAndZeroInputs::test_filter_tasks_by_on_empty_list_returns_empty PASSED [ 39%]
tests/test_pawpal.py::TestBoundaryConditions::test_task_duration_exactly_equal_to_time_remaining_is_scheduled PASSED [ 42%]
tests/test_pawpal.py::TestBoundaryConditions::test_high_priority_task_skipped_when_only_low_priority_fits PASSED [ 46%]
tests/test_pawpal.py::TestConflictDetection::test_touching_endpoints_are_not_flagged_as_conflict PASSED [ 50%]
tests/test_pawpal.py::TestConflictDetection::test_same_start_time_is_a_conflict PASSED [ 53%]
tests/test_pawpal.py::TestConflictDetection::test_partial_overlap_is_a_conflict PASSED [ 57%]
tests/test_pawpal.py::TestConflictDetection::test_cross_pet_overlap_is_detected PASSED [ 60%]
tests/test_pawpal.py::TestConflictDetection::test_warn_conflicts_returns_string_when_conflict_exists PASSED [ 64%]
tests/test_pawpal.py::TestRecurringEdgeCases::test_non_recurring_mark_complete_returns_none PASSED [ 67%]
tests/test_pawpal.py::TestRecurringEdgeCases::test_completing_already_completed_task_is_noop PASSED [ 71%]
tests/test_pawpal.py::TestRecurringEdgeCases::test_completing_nonexistent_title_returns_none PASSED [ 75%]
tests/test_pawpal.py::TestRecurringEdgeCases::test_completed_task_excluded_from_build_plan PASSED [ 78%]
tests/test_pawpal.py::TestDuplicateGuards::test_duplicate_task_title_is_ignored PASSED [ 82%]
tests/test_pawpal.py::TestDuplicateGuards::test_duplicate_pet_name_is_ignored PASSED [ 85%]
tests/test_pawpal.py::TestFiltering::test_filter_completed_false_excludes_done_tasks PASSED [ 89%]
tests/test_pawpal.py::TestFiltering::test_filter_completed_true_with_no_done_tasks_returns_empty PASSED [ 92%]
tests/test_pawpal.py::TestFiltering::test_filter_by_pet_name_returns_only_that_pets_tasks PASSED [ 96%]
tests/test_pawpal.py::TestFiltering::test_filter_with_no_kwargs_returns_original_list PASSED [100%]

============================== 28 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

The scheduling system is built around a handful of focused methods that each do one thing well. Here is what each one does and why it exists.

### Sorting

The primary sort happens inside `Scheduler.sort_tasks()`, which is called automatically every time `build_plan()` runs. It orders tasks by four criteria in sequence: priority first (high before medium before low), then whether the task's category matches one of the owner's stated preferences, then by pet name so that all of one pet's tasks cluster together rather than alternating, and finally by duration so that shorter tasks come first within a tie. The result is a schedule that front-loads the most important work and minimizes the mental overhead of switching between pets.

`Scheduler.sort_by_time()` is a separate, standalone utility that sorts purely by duration. It does not affect the plan — it's there for moments when you want to see tasks ranked from quickest to longest (or vice versa with `reverse=True`) outside the context of scheduling, such as when displaying a task list or doing a quick audit.

### Filtering

`Scheduler.filter_tasks()` is the internal time-budget gate: given a list of tasks and a number of minutes remaining, it returns only the tasks that would actually fit. This is what keeps the scheduler from trying to slot a 45-minute bath into a 10-minute gap.

`Scheduler.filter_tasks_by()` is the general-purpose filter for everyday queries. You can filter by completion status, by pet name, or both at once — all filters are optional and combine with AND logic, so omitting one simply skips that dimension. Filtering by pet name requires passing a `task_pet` mapping (a dict of `{id(task): pet_name}`) because tasks themselves do not store which pet they belong to.

### Conflict Detection

There are three methods here, each pitched at a different level of detail so callers can pick the one that fits their situation.

`Scheduler.find_conflicts()` is the foundation. It checks every unique pair of scheduled items and returns the ones whose time windows overlap, using the standard interval test: two slots overlap when `start_A < end_B` and `start_B < end_A`. This means items that share an endpoint — one ending at 08:30 and the next starting at 08:30 — are correctly treated as sequential, not conflicting. Both same-pet and cross-pet overlaps are caught.

`Scheduler.check_conflicts()` wraps `find_conflicts()` and returns a simple `True` or `False`. It exists for cases where you just need a yes-or-no answer and do not want to unpack a list of tuples.

`Scheduler.warn_conflicts()` is the lightest-weight option: it returns a ready-to-print warning string when problems exist, or `None` when the schedule is clean. Returning `None` rather than an empty string means callers can use a single truthiness check to decide whether to show anything at all.

When `build_plan()` finishes constructing a plan, it calls `find_conflicts()` on the result and stores each detected pair via `DailyPlan.add_conflict()`. Those stored conflicts flow through to `display()`, `explain()`, and `get_summary()` so that both the terminal output and the Streamlit UI can surface them without holding references to live objects.

### Recurring Tasks

When a task is marked done, `PetCareTask.mark_complete()` decides what happens next based on the task's `is_recurring` flag and `frequency` field. For a daily task it computes the next due date as `date.today() + timedelta(days=1)`; for a weekly task it uses `timedelta(days=7)`. It returns a brand-new `PetCareTask` instance carrying that due date. For a non-recurring task it simply returns `None`.

`Pet.complete_task()` is the method you actually call from outside. It finds the task by title, calls `mark_complete()` on it, removes the completed instance from the pet's task list, and — if a next-occurrence task was returned — appends the fresh copy in its place. The net effect is that recurring tasks automatically reappear on the list with an updated due date, while one-off tasks disappear once finished. Calling it on a title that does not exist or is already completed is a silent no-op, so it is safe to call without checking first.

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`) is split into four steps the owner works through from top to bottom:

- **Step 1 — Owner**: enter a name, set how many minutes are available today, and optionally pick preferred task categories (e.g. "nutrition", "hygiene") that get bumped ahead in the schedule within the same priority tier.
- **Step 2 — Add a Pet**: add as many pets as needed, each with a name, species, and age. Duplicate names are rejected automatically.
- **Step 3 — Add Tasks**: pick which pet gets the task, then fill in a title, duration, priority (low / medium / high), and category. Each pet's current task list renders as a sortable inline table — shortest tasks first — with a live total-time count and a ✕ button to remove any task on the spot.
- **Step 4 — Generate Schedule**: one click runs the scheduler and displays the full day plan as a formatted table (Time, Pet, Task, Duration, Priority), an expandable "Why this schedule?" explanation, any conflict warnings with per-conflict actionable tips, and a list of tasks that didn't fit with the reason why.

### Example workflow

1. Enter owner name **Jordan**, set **90 minutes** available, select **nutrition** as a preferred category. Click **Save Owner**.
2. Add pet **Buddy** (dog, age 3). Add pet **Mochi** (cat, age 5).
3. For Buddy, add: *Feeding* (10 min, high, nutrition), *Morning Walk* (30 min, high, exercise), *Bath Time* (45 min, medium, grooming).
4. For Mochi, add: *Feeding* (5 min, high, nutrition), *Litter Box Clean* (5 min, medium, hygiene).
5. Click **Generate Schedule**. The scheduler front-loads high-priority tasks, groups each pet's tasks together, inserts 5-minute breaks after every 60 minutes of work, and reports anything it couldn't fit.

### Key Scheduler behaviors demonstrated

- **Priority-first sort** — high-priority tasks always land before medium or low ones regardless of duration.
- **Preferred-category boost** — tasks in the owner's chosen categories move ahead of same-priority tasks in other categories.
- **Shortest-first display** — the Step 3 task list is sorted by `sort_by_time()` so owners see quickest tasks at the top.
- **Conflict detection** — `find_conflicts()` checks every pair of scheduled items for time-window overlap; detected conflicts surface as warning cards with the exact time window and a tip to shift one task.
- **Recurring due dates** — completing a daily task schedules the next occurrence for tomorrow; a weekly task lands 7 days out.
- **Skipped-task reporting** — tasks that don't fit include their priority icon (🔴 high, 🟡 medium, ⚪ low) and the reason.

### Sample CLI output (`python3 main.py`)

```
========================================
  DAILY: complete Buddy's Morning Walk
========================================
Before: [('Bath Time', None), ('Morning Walk', None), ('Feeding', None)]
After:  [('Bath Time', None), ('Feeding', None), ('Morning Walk', datetime.date(2026, 7, 6))]
  due_date = today + timedelta(days=1) = 2026-07-06

========================================
  SORT BY DURATION — shortest first
========================================
    5 min  [medium]  Litter Box Clean
    5 min  [high  ]  Feeding
   10 min  [high  ]  Feeding
   20 min  [medium]  Grooming
   30 min  [high  ]  Morning Walk
   45 min  [medium]  Bath Time

========================================
  FILTER — Buddy's tasks only
========================================
  [Buddy]  Bath Time  (todo)
  [Buddy]  Feeding  (todo)
  [Buddy]  Morning Walk  (todo)
  [Buddy]  Grooming  (todo)

========================================
       TODAY'S SCHEDULE
========================================
Daily Plan — 2026-07-05
------------------------------
08:00 - 08:10  [Buddy] Feeding
08:10 - 08:15  [Mochi] Feeding
08:15 - 08:45  [Buddy] Morning Walk
08:45 - 08:50  [Mochi] Litter Box Clean
08:50 - 09:10  [Buddy] Grooming

Skipped:
  [Buddy] Bath Time (not enough time remaining)

Total time used: 70 min
Tasks scheduled: 5
Tasks skipped:   1
Breaks inserted: 0
Conflicts:       0

========================================
  SAME-PET CONFLICT (08:00 overlap)
========================================
Warning: 1 scheduling conflict(s) detected:
  [Buddy] Morning Walk (08:00–08:30) overlaps [Buddy] Feeding (08:00–08:15)

========================================
  NO CONFLICT (sequential tasks)
========================================
warn_conflicts returned: None
```
