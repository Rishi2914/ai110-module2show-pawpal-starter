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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
