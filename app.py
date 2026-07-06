import streamlit as st
from pawpal_system import Owner, Pet, PetCareTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

CATEGORIES = ["exercise", "nutrition", "grooming", "hygiene", "general"]

if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Step 1: Owner ────────────────────────────────────────────────────────────
st.subheader("Step 1 — Owner")
owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)
preferences = st.multiselect(
    "Preferred task categories (bumped ahead within same priority tier)",
    CATEGORIES,
    default=[],
)

if st.button("Save Owner"):
    st.session_state.owner = Owner(owner_name, int(time_available), preferences)
    st.success(f"Owner '{owner_name}' saved with {time_available} min available.")

if st.session_state.owner is None:
    st.info("Save an owner to continue.")
    st.stop()

owner = st.session_state.owner

# ── Step 2: Add a Pet ────────────────────────────────────────────────────────
st.divider()
st.subheader("Step 2 — Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
col_species, col_age = st.columns(2)
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_age:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    existing_names = [p.name for p in owner.get_pets()]
    if pet_name in existing_names:
        st.warning(f"'{pet_name}' is already in your pet list.")
    else:
        owner.add_pet(Pet(pet_name, species, int(age)))
        st.success(f"Added {pet_name} the {species}, age {age}.")

pets = owner.get_pets()
if not pets:
    st.info("Add at least one pet to continue.")
    st.stop()

st.write("Pets:", ", ".join(f"{p.name} ({p.species}, age {p.age})" for p in pets))

# ── Step 3: Add Tasks ────────────────────────────────────────────────────────
st.divider()
st.subheader("Step 3 — Add Tasks")

pet_names = [p.name for p in pets]
selected_name = st.selectbox("Add task to", pet_names)
selected_pet = pets[pet_names.index(selected_name)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    category = st.selectbox("Category", CATEGORIES)

if st.button("Add Task"):
    existing_titles = [t.title for t in selected_pet.get_tasks()]
    if task_title in existing_titles:
        st.warning(f"'{task_title}' already exists for {selected_pet.name}.")
    else:
        selected_pet.add_task(PetCareTask(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            is_recurring=False,
            frequency="daily",
        ))
        st.success(f"Added '{task_title}' to {selected_pet.name}.")

for pet in pets:
    tasks = pet.get_tasks()
    if tasks:
        st.write(f"**{pet.name}'s tasks:**")
        header = st.columns([3, 1, 1, 1, 1, 1])
        header[0].caption("Title")
        header[1].caption("Duration")
        header[2].caption("Priority")
        header[3].caption("Category")
        header[4].caption("Due")
        header[5].caption("")
        for i, task in enumerate(tasks):
            row = st.columns([3, 1, 1, 1, 1, 1])
            row[0].write(task.title)
            row[1].write(f"{task.duration_minutes} min")
            row[2].write(task.priority)
            row[3].write(task.category)
            row[4].write(task.due_date.isoformat() if task.due_date else "—")
            if row[5].button("✕", key=f"rm_{pet.name}_{i}", help=f"Remove '{task.title}'"):
                pet.remove_task(task.title)
                st.rerun()

# ── Step 4: Generate Schedule ────────────────────────────────────────────────
st.divider()
st.subheader("Step 4 — Generate Schedule")

if st.button("Generate schedule"):
    all_tasks = [t for p in pets for t in p.get_tasks()]
    if not all_tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(start_time="08:00", time_limit_minutes=owner.time_available_minutes)
        plan = scheduler.build_plan(owner.get_pets(), owner)
        summary = plan.get_summary()

        st.success(f"Scheduled {summary['scheduled_count']} task(s) — {summary['total_duration_minutes']} min total")
        if summary["breaks_inserted"]:
            st.info(f"{summary['breaks_inserted']} × 5-min break(s) automatically included.")
        if summary["conflicts"]:
            st.error(f"{len(summary['conflicts'])} scheduling conflict(s) detected:")
            for c in summary["conflicts"]:
                st.caption(
                    f"• [{c['pet_a']}] {c['task_a']} ({c['start_a']}–{c['end_a']})"
                    f" overlaps [{c['pet_b']}] {c['task_b']} ({c['start_b']}–{c['end_b']})"
                )
        st.text(plan.display())

        st.subheader("Why this schedule?")
        st.text(plan.explain())

        if summary["skipped_count"] > 0:
            st.warning(f"{summary['skipped_count']} task(s) skipped due to time constraints.")
            for t in summary["skipped_tasks"]:
                st.caption(f"• [{t['pet']}] {t['title']} ({t['duration_minutes']} min) — {t['reason']}")
