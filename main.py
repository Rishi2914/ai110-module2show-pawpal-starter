from pawpal_system import Owner, Pet, PetCareTask, Scheduler

owner = Owner(name="Alex", time_available_minutes=90, preferences=["morning", "short sessions"])

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5)

dog.add_task(PetCareTask("Morning Walk",     30, "high",   "exercise",  True,  "daily"))
dog.add_task(PetCareTask("Feeding",          15, "high",   "nutrition", True,  "daily"))
dog.add_task(PetCareTask("Bath Time",        20, "medium", "grooming",  False, "weekly"))

cat.add_task(PetCareTask("Feeding",          10, "high",   "nutrition", True,  "daily"))
cat.add_task(PetCareTask("Litter Box Clean", 10, "medium", "hygiene",   True,  "daily"))
cat.add_task(PetCareTask("Playtime",         15, "low",    "exercise",  False, "daily"))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(start_time="08:00", time_limit_minutes=owner.time_available_minutes)
plan = scheduler.build_plan(owner.get_pets(), owner)

print("=" * 40)
print("       TODAY'S SCHEDULE")
print("=" * 40)
print(plan.display())
print()
print(plan.explain())
print()
summary = plan.get_summary()
print(f"Total time used: {summary['total_duration_minutes']} min")
print(f"Tasks scheduled: {summary['scheduled_count']}")
print(f"Tasks skipped:   {summary['skipped_count']}")
