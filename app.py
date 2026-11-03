import streamlit as st
from src.ui.inputs import render_inputs

st.set_page_config(
    page_title="ExamAce",
    page_icon="📚",
    layout="wide",
)

st.title("ExamAce — AI Study Planner")

answers, budget = render_inputs()

completed = all(answer is not None for answer in answers)

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
    st.info("Study plan generation will be connected to the optimizer later.")
    