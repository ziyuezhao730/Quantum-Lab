
import json
from pathlib import Path

import streamlit as st


def clear_previous_plan():
    st.session_state.pop("plan", None)


def load_diagnostic_questions():
    """Load approved diagnostic questions from the course data."""
    course_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "demo"
        / "course.json"
    )

    with course_path.open("r", encoding="utf-8") as file:
        course = json.load(file)

    topics = {
        topic["topic_id"]: topic["name"]
        for topic in course["topics"]
    }

    questions = [
        question
        for question in course["questions"]
        if question["purpose"] == "diagnostic"
        and question["review_status"] == "approved"
    ]

    return questions, topics


def render_inputs():
    st.header("ExamAce - Diagnostic Quiz")

    questions, topics = load_diagnostic_questions()
    answers = {}

    for i, question in enumerate(questions):
        topic_name = topics[question["topic_id"]]

        st.subheader(f"Question {i + 1} — {topic_name}")

        answer = st.radio(
            question["text"],
            options=list(question["choices"].keys()),
            format_func=lambda choice, q=question: (
                f"{choice}. {q['choices'][choice]}"
            ),
            index=None,
            key=f"question_{question['question_id']}",
            on_change=clear_previous_plan,
        )

        answers[question["question_id"]] = answer

    budget = st.number_input(
        "How many minutes can you study?",
        min_value=0,
        max_value=180,
        value=60,
        step=5,
        on_change=clear_previous_plan,
    )

    return answers, budget
