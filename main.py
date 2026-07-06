from pawpal_system import Owner, Pet, PetCareTask, Scheduler, ScheduledItem

owner = Owner(name="Alex", time_available_minutes=90, preferences=["nutrition", "hygiene"])

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5)

# tasks added intentionally out of priority/duration order
dog.add_task(PetCareTask("Bath Time",        45, "medium", "grooming",  False, "weekly"))  # non-recurring
dog.add_task(PetCareTask("Morning Walk",     30, "high",   "exercise",  True,  "daily"))
dog.add_task(PetCareTask("Feeding",          10, "high",   "nutrition", True,  "daily"))

cat.add_task(PetCareTask("Playtime",         20, "low",    "exercise",  False, "daily"))
cat.add_task(PetCareTask("Litter Box Clean",  5, "medium", "hygiene",   True,  "daily"))
cat.add_task(PetCareTask("Feeding",           5, "high",   "nutrition", True,  "daily"))

owner.add_pet(dog)
owner.add_pet(cat)

# ── due_date via timedelta — recurring daily ──────────────────────────────────
print("=" * 40)
print("  DAILY: complete Buddy's Morning Walk")
print("=" * 40)
print("Before:", [(t.title, t.due_date) for t in dog.get_tasks()])
next_walk = dog.complete_task("Morning Walk")
print("After: ", [(t.title, t.due_date) for t in dog.get_tasks()])
print(f"  due_date = today + timedelta(days=1) = {next_walk.due_date}")

# ── due_date via timedelta — recurring weekly ─────────────────────────────────
print()
print("=" * 40)
print("  WEEKLY: complete Buddy's Grooming")
print("         (is_recurring=True, frequency='weekly')")
print("=" * 40)
dog.add_task(PetCareTask("Grooming", 20, "medium", "grooming", True, "weekly"))
next_groom = dog.complete_task("Grooming")
print(f"  due_date = today + timedelta(days=7) = {next_groom.due_date}")

# ── non-recurring: no due date assigned ───────────────────────────────────────
print()
print("=" * 40)
print("  NON-RECURRING: complete Mochi's Playtime (is_recurring=False)")
print("=" * 40)
next_play = cat.complete_task("Playtime")
print(f"  returned: {next_play}  (None — no next occurrence, no due date)")

scheduler = Scheduler(start_time="08:00", time_limit_minutes=owner.time_available_minutes)

all_tasks = [t for pet in owner.get_pets() for t in pet.get_tasks()]
task_pet = {id(t): pet.name for pet in owner.get_pets() for t in pet.get_tasks()}

# ── sort_by_time ─────────────────────────────────────────────────────────────
print("=" * 40)
print("  SORT BY DURATION — shortest first")
print("=" * 40)
by_duration = scheduler.sort_by_time(all_tasks)
for t in by_duration:
    print(f"  {t.duration_minutes:3d} min  [{t.priority:6s}]  {t.title}")

print()
print("=" * 40)
print("  SORT BY DURATION — longest first")
print("=" * 40)
by_duration_desc = scheduler.sort_by_time(all_tasks, reverse=True)
for t in by_duration_desc:
    print(f"  {t.duration_minutes:3d} min  [{t.priority:6s}]  {t.title}")

# ── filter_tasks_by — completion status ──────────────────────────────────────
print()
print("=" * 40)
print("  FILTER — incomplete tasks only")
print("=" * 40)
incomplete = scheduler.filter_tasks_by(all_tasks, completed=False)
for t in incomplete:
    print(f"  {'done' if t.completed else 'todo'}  {t.title}")

print()
print("=" * 40)
print("  FILTER — completed tasks only")
print("=" * 40)
done = scheduler.filter_tasks_by(all_tasks, completed=True)
for t in done:
    print(f"  done  {t.title}")
if not done:
    print("  (none)")

# ── filter_tasks_by — pet name ───────────────────────────────────────────────
print()
print("=" * 40)
print("  FILTER — Buddy's tasks only")
print("=" * 40)
buddy_tasks = scheduler.filter_tasks_by(all_tasks, task_pet, pet_name="Buddy")
for t in buddy_tasks:
    print(f"  [{task_pet[id(t)]}]  {t.title}  ({'done' if t.completed else 'todo'})")

print()
print("=" * 40)
print("  FILTER — Mochi, incomplete only")
print("=" * 40)
mochi_incomplete = scheduler.filter_tasks_by(all_tasks, task_pet, completed=False, pet_name="Mochi")
for t in mochi_incomplete:
    print(f"  [{task_pet[id(t)]}]  {t.title}")

# ── conflict detection — no conflict (normal sequential plan) ─────────────────
print()
print("=" * 40)
print("       TODAY'S SCHEDULE")
print("=" * 40)
plan = scheduler.build_plan(owner.get_pets(), owner)
print(plan.display())
print()
print(plan.explain())
print()
summary = plan.get_summary()
print(f"Total time used: {summary['total_duration_minutes']} min")
print(f"Tasks scheduled: {summary['scheduled_count']}")
print(f"Tasks skipped:   {summary['skipped_count']}")
print(f"Breaks inserted: {summary['breaks_inserted']}")
print(f"Conflicts:       {len(summary['conflicts'])}")

# ── warn_conflicts: two tasks at the exact same time ─────────────────────────
print()
print("=" * 40)
print("  SAME-PET CONFLICT (08:00 overlap)")
print("=" * 40)
# Buddy has Morning Walk and Feeding both starting at 08:00
walk   = ScheduledItem(PetCareTask("Morning Walk", 30, "high",   "exercise",  True, "daily"),
                       "08:00", "08:30", "scheduled", "Buddy")
feed_b = ScheduledItem(PetCareTask("Feeding",      15, "high",   "nutrition", True, "daily"),
                       "08:00", "08:15", "scheduled", "Buddy")

warning = scheduler.warn_conflicts([walk, feed_b])
print(warning)

print()
print("=" * 40)
print("  CROSS-PET CONFLICT (08:00 overlap)")
print("=" * 40)
# Mochi's Feeding also starts at 08:00, clashing with Buddy's Morning Walk
feed_m = ScheduledItem(PetCareTask("Feeding",      10, "high",   "nutrition", True, "daily"),
                       "08:00", "08:10", "scheduled", "Mochi")

warning = scheduler.warn_conflicts([walk, feed_m])
print(warning)

print()
print("=" * 40)
print("  NO CONFLICT (sequential tasks)")
print("=" * 40)
# Feeding starts exactly when Morning Walk ends — touching, not overlapping
feed_seq = ScheduledItem(PetCareTask("Feeding",    15, "high",   "nutrition", True, "daily"),
                         "08:30", "08:45", "scheduled", "Buddy")

warning = scheduler.warn_conflicts([walk, feed_seq])
print(f"warn_conflicts returned: {warning}")   # expected: None → no warning printed
