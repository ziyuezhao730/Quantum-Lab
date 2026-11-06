import streamlit as st


def render_results(scores, allocation):
    st.header("your study plan")
    st.subheader("Initial topic score from two questions")
    st.caption("a coarse initial signal, not a mastery estimate or grade prediction")
    cols=st.columns(3)
    for col,(topic,score) in zip(cols,scores.items()):
        col.metric(topic,f"{score:.0%}")
    st.subheader("recommended study time")
    for topic,minutes in allocation.items():
        st.write(f"**{topic}** - {minutes} minutes")
    st.caption("exact classical optimization, utility is a study-priority heuristic")


def render_practice_questions(questions):
    st.subheader("targeted practice")
    for q in questions:
        with st.container(border=True):
            st.write(q["text"])
            st.caption(f"{q['topic']} - difficulty {q['difficulty']} - {q['source']}, page {q['page']}")
            st.caption(q["reason"])
            if q["answer"] is None:
                st.info("answer unavailable")
            else:
                with st.expander("show answer"):
                    st.write(q["answer"])
