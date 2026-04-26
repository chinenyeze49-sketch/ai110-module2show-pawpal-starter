"""PawPal+ Streamlit UI — full smart scheduling interface + AI features."""

import os
from datetime import datetime, timedelta

import streamlit as st

from ai_assistant import answer_care_question, explain_plan, suggest_tasks
from logging_config import configure_logging
from pawpal_system import Owner, Pet, Scheduler, Task

configure_logging()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption(
    f"AI provider: **{os.environ.get('PAWPAL_AI_PROVIDER', 'mock')}** "
    f"(set PAWPAL_AI_PROVIDER=anthropic and ANTHROPIC_API_KEY for real LLM calls)"
)

if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json()

# ── Owner setup ─────────────────────────────────────────────────────────────
with st.expander("👤 Owner setup", expanded=st.session_state.owner is None):
    owner_name = st.text_input("Your name", value="Alex Rivera")
    owner_email = st.text_input("Email", value="alex@example.com")
    owner_phone = st.text_input("Phone", value="555-0100")
    col1, col2 = st.columns(2)
    if col1.button("Set owner"):
        try:
            st.session_state.owner = Owner(
                name=owner_name, email=owner_email, phone=owner_phone
            )
            st.success(f"Owner set: {owner_name}")
        except ValueError as e:
            st.error(str(e))
    if col2.button("Save data"):
        if st.session_state.owner:
            st.session_state.owner.save_to_json()
            st.success("Saved to data.json")

if st.session_state.owner is None:
    st.info("Set an owner above to get started.")
    st.stop()

owner = st.session_state.owner

# ── Pet setup ───────────────────────────────────────────────────────────────
st.subheader("🐶 Add a pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Buddy")
    pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
with col2:
    pet_breed = st.text_input("Breed", value="Labrador")
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    try:
        owner.add_pet(Pet(name=pet_name, species=pet_species,
                          breed=pet_breed, age=int(pet_age)))
        st.success(f"Added {pet_name} the {pet_species}!")
    except ValueError as e:
        st.error(str(e))

if owner.get_pets():
    st.write("Your pets:", [p.name for p in owner.get_pets()])
else:
    st.info("No pets yet.")

# ── Tabs: scheduling vs AI ──────────────────────────────────────────────────
tab_schedule, tab_ai_explain, tab_ai_suggest, tab_ai_qa = st.tabs(
    ["🗓 Schedule", "🤖 Explain plan", "🤖 Suggest tasks", "🤖 Care Q&A"]
)

# ── Schedule tab ────────────────────────────────────────────────────────────
with tab_schedule:
    st.subheader("Add a task")
    if not owner.get_pets():
        st.warning("Add a pet first before scheduling tasks.")
    else:
        pet_names = [p.name for p in owner.get_pets()]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        selected_pet = next(p for p in owner.get_pets()
                            if p.name == selected_pet_name)

        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            task_type = st.selectbox(
                "Type", ["feeding", "walk", "medication", "appointment"]
            )
        with col2:
            task_hour = st.number_input("Hour (0-23)", 0, 23, 8)
            task_priority = st.number_input("Priority (1=highest)", 1, 5, 1)

        is_recurring = st.checkbox("Recurring daily?")
        if st.button("Add task"):
            try:
                due = datetime.today().replace(
                    hour=int(task_hour), minute=0, second=0, microsecond=0
                )
                selected_pet.add_task(Task(
                    title=task_title,
                    task_type=task_type,
                    due_time=due,
                    priority=int(task_priority),
                    is_recurring=is_recurring,
                    recurrence_interval=(timedelta(days=1)
                                         if is_recurring else None),
                ))
                st.success(f"Task '{task_title}' added to {selected_pet_name}!")
            except ValueError as e:
                st.error(str(e))

    st.divider()
    st.subheader("Today's schedule")
    sort_option = st.radio("Sort by", ["Priority", "Time"], horizontal=True)
    filter_option = st.radio(
        "Show", ["All", "Pending only", "Completed only"], horizontal=True
    )

    if st.button("Generate schedule"):
        scheduler = Scheduler(owner=owner)
        tasks = (scheduler.sort_by_priority()
                 if sort_option == "Priority" else scheduler.sort_by_time())
        if filter_option == "Pending only":
            tasks = [t for t in tasks if not t.is_completed]
        elif filter_option == "Completed only":
            tasks = [t for t in tasks if t.is_completed]

        if not tasks:
            st.info("No tasks to show.")
        else:
            st.markdown("### Schedule")
            for t in tasks:
                color = {1: "🔴", 2: "🟡"}.get(t.priority, "🟢")
                icon = {"feeding": "🍖", "walk": "🦮",
                        "medication": "💊", "appointment": "🏥"}.get(
                    t.task_type, "📌"
                )
                status = "✓" if t.is_completed else "○"
                st.markdown(
                    f"{color} {icon} **{t.due_time.strftime('%H:%M')}** | "
                    f"Priority {t.priority} | {t.title} | "
                    f"`{t.task_type}` | {status}"
                )

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("Scheduling conflicts detected:")
            for t in conflicts:
                st.markdown(
                    f"- **{t.title}** @ {t.due_time.strftime('%H:%M')} "
                    f"— within 30 mins of another task"
                )
        else:
            st.success("No scheduling conflicts!")

# ── AI: explain the plan ────────────────────────────────────────────────────
with tab_ai_explain:
    st.write(
        "Generates a natural-language explanation of today's plan: which task "
        "comes first, why, and any conflict callouts."
    )
    if st.button("🤖 Explain today's plan"):
        scheduler = Scheduler(owner=owner)
        with st.spinner("Asking the AI..."):
            resp = explain_plan(scheduler)
        st.markdown(resp.text)
        st.caption(
            f"provider: `{resp.source}` · confidence: {resp.confidence:.2f}"
            + (f" · guardrail: {resp.guardrail}" if resp.guardrail else "")
        )

# ── AI: suggest tasks ───────────────────────────────────────────────────────
with tab_ai_suggest:
    st.write(
        "Generates a starter set of care tasks tailored to a specific pet. "
        "Useful when you've just added a new pet and want a default schedule."
    )
    if not owner.get_pets():
        st.warning("Add a pet first.")
    else:
        pet_names = [p.name for p in owner.get_pets()]
        target_name = st.selectbox("Suggest tasks for", pet_names,
                                   key="suggest_target")
        if st.button("🤖 Suggest tasks"):
            target_pet = next(p for p in owner.get_pets()
                              if p.name == target_name)
            with st.spinner("Asking the AI..."):
                resp = suggest_tasks(target_pet)
            st.markdown(resp.text)
            st.caption(
                f"provider: `{resp.source}` · confidence: {resp.confidence:.2f}"
            )

# ── AI: care Q&A ────────────────────────────────────────────────────────────
with tab_ai_qa:
    st.write(
        "Open-ended pet-care questions. Vet/medical questions are intentionally "
        "redirected — PawPal+ is a planning assistant, not a vet."
    )
    question = st.text_input(
        "Your question",
        value="How often should I bathe my Siamese cat?",
        key="qa_input",
    )
    if st.button("🤖 Ask PawPal"):
        with st.spinner("Asking the AI..."):
            resp = answer_care_question(question)
        if resp.guardrail == "vet_redirect":
            st.warning(resp.text)
        else:
            st.markdown(resp.text)
        st.caption(
            f"provider: `{resp.source}` · confidence: {resp.confidence:.2f}"
            + (f" · guardrail: {resp.guardrail}" if resp.guardrail else "")
        )
