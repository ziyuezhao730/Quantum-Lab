import streamlit as st


def render_results(scores, allocation):
    st.header("Your Personalized Study Plan")

    st.subheader("Diagnostic Scores")

    for topic, score in scores.items():
        st.write(f"**{topic}** — {score:.0%}")
        st.progress(float(score))

    st.subheader("Recommended Study Time")

    total_minutes = sum(allocation.values())
    st.metric("Total Study Time", f"{total_minutes} minutes")

    for topic, minutes in allocation.items():
        st.write(f"**{topic}** — {minutes} minutes")

    st.bar_chart(allocation)


def render_practice_questions(questions):
    st.subheader("Recommended Practice Questions")

    for i, question in enumerate(questions):
        with st.container(border=True):
            st.write(f"**Question {i + 1}: {question['text']}**")

            st.caption(f"Source: {question['source']}")

            with st.expander("Show Answer"):
                st.write(question["answer"])