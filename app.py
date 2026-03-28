"""PawPal+ Streamlit UI — full smart scheduling interface."""

import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    loaded = Owner.load_from_json()
    st.session_state.owner = loaded

# ── Owner ─────────────────────────────────────────────────────────────────────
st.subheader("Owner")
owner_name = st.text_input("Your name", value="Alex Rivera")
owner_email = st.text_input("Email", value="alex@example.com")
owner_phone = st.text_input("Phone", value="555-0100")

if st.button("Set Owner"):
    st.session_state.owner = Owner(name=owner_name, email=owner_email, phone=owner_phone)
    st.success(f"Owner set: {owner_name}")

if st.button("💾 Save Data"):
    if st.session_state.owner:
        st.session_state.owner.save_to_json()
        st.success("Data saved to data.json!")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner = st.session_state.owner

# ── Add a Pet ─────────────────────────────────────────────────────────────────
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

# ── Add a Task ────────────────────────────────────────────────────────────────
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

# ── Schedule ──────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

sort_option = st.radio("Sort by", ["Priority", "Time"], horizontal=True)
filter_option = st.radio("Show", ["All", "Pending only", "Completed only"], horizontal=True)

if st.button("Generate Schedule"):
    scheduler = Scheduler(owner=owner)

    if sort_option == "Priority":
        tasks = scheduler.sort_by_priority()
    else:
        tasks = scheduler.sort_by_time()

    if filter_option == "Pending only":
        tasks = [t for t in tasks if not t.is_completed]
    elif filter_option == "Completed only":
        tasks = [t for t in tasks if t.is_completed]

    if not tasks:
        st.info("No tasks to show.")
    else:
        table_data = [
            {
                "Time": t.due_time.strftime("%H:%M"),
                "Priority": t.priority,
                "Task": t.title,
                "Type": t.task_type,
                "Done": "✓" if t.is_completed else "○",
            }
            for t in tasks
        ]
        st.table(table_data)

    # Conflict warnings
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning("⚠ Scheduling conflicts detected:")
        for t in conflicts:
            st.markdown(f"- **{t.title}** @ {t.due_time.strftime('%H:%M')} — within 30 mins of another task")
    else:
        st.success("No scheduling conflicts!")
