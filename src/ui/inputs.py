
import streamlit as st


def clear_previous_plan():
    st.session_state.pop("plan", None)


def load_diagnostic_questions(course):
    questions=[q.model_dump() for q in course.questions if q.purpose=="diagnostic" and q.review_status=="approved"]
    topics={t.topic_id:t.name for t in course.topics}
    return questions,topics


def render_inputs(course):
    st.header("ExamAce - Diagnostic Quiz")

    questions, topics = load_diagnostic_questions(course)
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
        step=1,
        key="budget",
        on_change=clear_previous_plan,
    )

    return answers, budget
