"""one diagnostic dialog per browser session, reopenable"""
import streamlit as st
from src.intelligence.assess import score_diagnostic


def clear_plan():
    st.session_state.pop("study_plan",None)
    st.session_state.pop("experiment",None)


def dismiss_diagnostic():
    st.session_state["diag_open"]=False


def open_diagnostic():
    clear_plan()
    st.session_state["diag_open"]=True
    st.session_state["diag_step"]=0
    st.session_state["diag_answers"]={}
    st.session_state.pop("proficiency",None)
    for key in list(st.session_state):
        if key.startswith("diag_choice_"):
            del st.session_state[key]


def save_answer(qid,key):
    st.session_state["diag_answers"][qid]=st.session_state[key]
    clear_plan()


@st.dialog("Find your starting point",width="large",on_dismiss=dismiss_diagnostic)
def diagnostic_dialog(course):
    questions=[q for q in course.questions if q.purpose=="diagnostic" and q.review_status=="approved"]
    step=st.session_state.get("diag_step",0)
    answers=st.session_state.setdefault("diag_answers",{})
    q=questions[step]
    names={t.topic_id:t.name for t in course.topics}
    st.caption(f"QUESTION {step+1} OF {len(questions)} · {names[q.topic_id]}")
    st.progress((step+1)/len(questions))
    st.markdown(f"### {q.text}")
    choices=list(q.choices)
    selected=answers.get(q.question_id)
    key=f"diag_choice_{q.question_id}"
    st.radio("Choose an answer",choices,index=choices.index(selected) if selected in choices else None,format_func=lambda choice:f"{choice}. {q.choices[choice]}",key=key,on_change=save_answer,args=(q.question_id,key))
    left,right=st.columns(2)
    if step and left.button("Back",key="diag_back",use_container_width=True):
        st.session_state["diag_step"]=step-1
        st.rerun()
    label="Finish diagnostic" if step==len(questions)-1 else "Next question"
    if right.button(label,key="diag_next",disabled=answers.get(q.question_id) is None,type="primary",use_container_width=True):
        if step==len(questions)-1:
            result=score_diagnostic(course,answers)
            st.session_state["proficiency"]=result.proficiency
            st.session_state["diag_open"]=False
        else:
            st.session_state["diag_step"]=step+1
        st.rerun()
