import streamlit as st
from src.ui.inputs import render_inputs
from src.ui.results import render_results, render_practice_questions

st.set_page_config(
    page_title="ExamAce",
    page_icon="📚",
    layout="wide",
)

st.title("ExamAce — AI Study Planner")

answers, budget = render_inputs()

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
        "DEMO MODE: The results below are sample data, "
        "not generated from your answers."
    )

    demo_scores = {
        "Algebra": 0.6,
        "Calculus": 0.8,
        "Probability": 0.4,
    }

    demo_allocation = {
        "Algebra": 30,
        "Calculus": 10,
        "Probability": 20,
    }

    demo_questions = [
        {
            "text": "Solve: 2x + 3 = 11",
            "source": "Demo Question Bank",
            "answer": "x = 4",
        },
        {
            "text": "What is the derivative of x²?",
            "source": "Demo Question Bank",
            "answer": "2x",
        },
    ]

    render_results(demo_scores, demo_allocation)
    render_practice_questions(demo_questions)
    