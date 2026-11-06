import streamlit as st
import json
from src.ui.inputs import render_inputs
from src.ui.results import render_results, render_practice_questions
from src.ui.planner_adapter import (
    load_course_data,
    get_topic_weights,
    get_topic_names,
    get_practice_questions,
)
from src.optimizer.classical import solve_exact

st.set_page_config(
    page_title="ExamAce",
    page_icon="📚",
    layout="wide",
)

st.title("ExamAce — AI Study Planner")

answers, budget = render_inputs()

# Invalidate the old plan if the inputs change
if "plan" in st.session_state:
    old_plan = st.session_state["plan"]

    if (
        old_plan["answers"] != answers
        or old_plan["budget"] != budget
    ):
        del st.session_state["plan"]

completed = len(answers) == 6 and all(
    answer is not None for answer in answers.values()
)

if not completed:
    st.warning("Please answer all 6 questions before continuing.")

generate = st.button(
    "Generate Study Plan",
    disabled=not completed,
)

if generate:
    st.session_state["plan"] = {
        "answers": answers.copy(),
        "budget": budget,
    }

if "plan" in st.session_state:
    plan = st.session_state["plan"]

    st.subheader("Diagnostic Submission")
    st.write("Your answers:", plan["answers"])
    st.write("Study budget:", plan["budget"], "minutes")
    st.warning(
        "TEST MODE: Study time is calculated by the real optimizer, "
        "but proficiency scores are fixed test values, "
        "not calculated from your answers."
    )

    course = load_course_data()
    weights = get_topic_weights(course)
    topic_names = get_topic_names(course)

    # Temporary test proficiency — NOT calculated from answers
    test_proficiency = {
        "T1": 1.0,
        "T2": 0.0,
        "T3": 0.5,
    }

    result = solve_exact(
        weights,
        test_proficiency,
        plan["budget"],
    )

    demo_scores = {
        topic_names[topic_id]: score
        for topic_id, score in test_proficiency.items()
    }

    demo_allocation = {
        topic_names[topic_id]: minutes
        for topic_id, minutes in result["allocations"].items()
    }

    practice_questions = get_practice_questions(course)

    render_results(demo_scores, demo_allocation)
    st.subheader("Optimization Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Used Time", f"{result['used_minutes']} min")

    with col2:
        st.metric("Unused Time", f"{result['unused_minutes']} min")

    with col3:
        st.metric("Utility", f"{result['utility']:.3f}")

    st.caption(
        f"Solver: {result['actual_solver']} | "
        f"Execution: {result['execution_mode']} | "
        f"Feasible: {result['feasible']}"
    )
    render_practice_questions(practice_questions)
    
        # Create a snapshot of the current study plan
    snapshot = {
        "answers": plan["answers"],
        "budget_minutes": plan["budget"],
        "proficiency": test_proficiency,
        "allocations": result["allocations"],
        "used_minutes": result["used_minutes"],
        "unused_minutes": result["unused_minutes"],
        "utility": result["utility"],
        "actual_solver": result["actual_solver"],
        "execution_mode": result["execution_mode"],
        "feasible": result["feasible"],
        "test_mode": True,
    }

    st.subheader("Download Study Plan")

    st.download_button(
        label="Download Snapshot JSON",
        data=json.dumps(snapshot, indent=2),
        file_name="examace_snapshot.json",
        mime="application/json",
    )