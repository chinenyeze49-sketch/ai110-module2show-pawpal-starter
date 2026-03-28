"""PawPal+ Streamlit UI — connected to pawpal_system.py logic layer."""

import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Step 2: Session state memory ──────────────────────────────────────────────
# Streamlit reruns top-to-bottom on every interaction.
# We store the Owner object in session_state so it persists between clicks.
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Owner setup ───────────────────────────────────────────────────────────────
st.subheader("Owner")
owner_name = st.text_input("Your name", value="Alex Rivera")
owner_email = st.text_input("Email", value="alex@example.com")
owner_phone = st.text_input("Phone", value="555-0100")

if st.button("Set Owner"):
    st.session_state.owner = Owner(
        name=owner_name,
        email=owner_email,
        phone=owner_phone,
    )
    st.success(f"Owner set: {owner_name}")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner = st.session_state.owner

# ── Step 3: Add a Pet ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a Pet")

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Buddy")
    pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
with col2:
    pet_breed = st.text_input("Breed", value="Labrador")
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    pet = Pet(name=pet_name, species=pet_species, breed=pet_breed, age=int(pet_age))
    owner.add_pet(pet)
    st.success(f"Added {pet_name} the {pet_species}!")

if owner.get_pets():
    st.write("Your pets:", [p.name for p in owner.get_pets()])
else:
    st.info("No pets yet.")

# ── Step 3: Add a Task ────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a Task")

if not owner.get_pets():
    st.warning("Add a pet first before scheduling tasks.")
else:
    pet_names = [p.name for p in owner.get_pets()]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)
    selected_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_type = st.selectbox("Type", ["feeding", "walk", "medication", "appointment"])
    with col2:
        task_hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=8)
        task_priority = st.number_input("Priority (1=highest)", min_value=1, max_value=5, value=1)

    is_recurring = st.checkbox("Recurring daily?")

    if st.button("Add Task"):
        due = datetime.today().replace(hour=int(task_hour), minute=0, second=0, microsecond=0)
        task = Task(
            title=task_title,
            task_type=task_type,
            due_time=due,
            priority=int(task_priority),
            is_recurring=is_recurring,
            recurrence_interval=timedelta(days=1) if is_recurring else None,
        )
        selected_pet.add_task(task)
        st.success(f"Task '{task_title}' added to {selected_pet_name}!")

# ── Generate Schedule ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

if st.button("Generate Schedule"):
    scheduler = Scheduler(owner=owner)
    todays_tasks = scheduler.sort_by_priority()

    if not todays_tasks:
        st.info("No tasks due today.")
    else:
        for task in todays_tasks:
            status = "✓" if task.is_completed else "○"
            st.markdown(
                f"**[{status}] {task.due_time.strftime('%H:%M')}** "
                f"| Priority {task.priority} | {task.title} `{task.task_type}`"
            )

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("⚠ Conflicts detected:")
            for t in conflicts:
                st.markdown(f"- {t.title} @ {t.due_time.strftime('%H:%M')}")
        else:
            st.success("No scheduling conflicts!")

