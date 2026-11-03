import streamlit as st
def clear_previous_plan():
    st.session_state.pop("plan", None)


def render_inputs():
    st.header("ExamAce - Diagnostic Quiz")

    answers = []

    for i in range(6):
        answer = st.radio(
            f"Question {i + 1}",
            ["A", "B", "C", "D"],
            index=None,
            key=f"question_{i}",
            on_change=clear_previous_plan,
        )

        answers.append(answer)

    budget = st.number_input(
        "How many minutes can you study?",
        min_value=0,
        max_value=180,
        value=60,
        step=5,
        on_change=clear_previous_plan,
    )

    return answers, budget
    