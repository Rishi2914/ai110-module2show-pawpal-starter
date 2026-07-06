# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  Five classes — Owner, Pet, PetCareTask, Scheduler, and DailyPlan — covering owner/pet data, task definitions, scheduling logic, and the resulting plan.

- What classes did you include, and what responsibilities did you assign to each?
  Owner held time and preferences; Pet held a task list; PetCareTask stored task metadata; Scheduler built the plan; DailyPlan stored results and the explain output.

**b. Design changes**

Several attributes and methods were missing from the initial design and added during implementation.

`PetCareTask` gained `completed` and `due_date` fields plus `mark_complete()` once recurring task logic was added. `Scheduler` gained `sort_by_time()`, `filter_tasks_by()`, `find_conflicts()`, and `warn_conflicts()` as the sorting, filtering, and conflict-detection features were built out. `DailyPlan` gained `breaks_inserted` and `conflicts` when break insertion and conflict recording were introduced. `ScheduledItem` gained `pet_name` so conflict cards could identify which pet each item belonged to.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  It considers the owner's available time, each task's priority (high/medium/low), the owner's preferred categories, and each task's duration.

- How did you decide which constraints mattered most?
  Time is a hard limit — a task that doesn't fit is skipped entirely. Priority and preferences are soft ordering rules applied before the time check so the most important tasks land first.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  The greedy single-pass never evicts a scheduled low-priority task to make room for a high-priority one that arrived later in the sort order — so a high-priority task can be skipped while a lower-priority task stays in.

- Why is that tradeoff reasonable for this scenario?
  A backtracking or knapsack approach that considers evictions is O(2ⁿ) versus O(n log n) for the current sort-then-fill pass — acceptable correctness gap for daily pet care where task counts rarely exceed 10–15.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  AI was used to implement algorithmic methods (sorting, conflict detection, recurring due dates), write docstrings, generate the test suite, and update the README and UML diagram to match the final code.

- What kinds of prompts or questions were most helpful?
  Concrete, scoped prompts worked best — asking for a single method with a specific signature and behavior produced cleaner output than open-ended "improve the scheduler" requests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  When the `timedelta` due-date change was first suggested, the generated edit was interrupted because the proposed change to `PetCareTask.__init__` used `_date | None` union syntax, which fails on Python 3.9 without `from __future__ import annotations`.

- How did you evaluate or verify what the AI suggested?
  Running the tests caught the `TypeError` immediately; the fix (`from __future__ import annotations`) was verified by re-running the full 28-case suite and confirming all passed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  Priority ordering, preferred-category scheduling, recurring due dates (daily +1 day, weekly +7 days), conflict detection (overlap vs touching endpoints, cross-pet), duplicate guards, filtering by completion status and pet name, and edge cases like zero available time and an empty task list.

- Why were these tests important?
  These are the behaviors that could silently produce a wrong schedule — a misranked priority or an off-by-one on the due date wouldn't raise an error, only produce bad output.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  High confidence for the cases covered; the 28 tests all pass and span the main happy paths and edge cases.

- What edge cases would you test next if you had more time?
  A task whose duration equals the break threshold exactly, and schedules where all tasks are the same priority and duration to verify the pet-grouping tiebreaker.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  The conflict detection design — using three methods (`find_conflicts`, `check_conflicts`, `warn_conflicts`) at different levels of detail so callers can pick the right one for their context.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  Add a proper task ID instead of relying on `id(task)` as a dict key, and persist owner/pet/task data to a file so the Streamlit session survives a page refresh.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  Small, well-named methods with a single responsibility are much easier to test and to hand to an AI for iteration than large methods that mix concerns — the time spent on clean interfaces paid off every time a new feature needed to plug in.
