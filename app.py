"""diagnostic to exact plan, targeted practice & validated profile export"""
from pathlib import Path

import streamlit as st

from src.contracts import PlanRequest
from src.intelligence.assess import score_diagnostic
from src.intelligence.pipeline import load_course, make_snapshot
from src.intelligence.rank import select_questions
from src.optimizer.classical import solve_plan
from src.ui.inputs import render_inputs
from src.ui.results import render_results, render_practice_questions

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="ExamAce",page_icon="📚",layout="wide")
st.title("ExamAce")
st.caption("a short diagnostic, a study plan & source-linked practice")
try:
    course=load_course(ROOT/"data/demo/course.json")
except (ValueError,OSError) as error:
    st.error(f"course data could not be loaded - {error}")
    st.stop()

answers,budget=render_inputs(course)
completed=all(answer is not None for answer in answers.values())
if not completed:
    st.info("answer all six questions to generate a plan")
if st.button("generate study plan",disabled=not completed,key="generate"):
    try:
        diagnostic=score_diagnostic(course,answers)
        request=PlanRequest(budget_minutes=budget,proficiency=diagnostic.proficiency,requested_solver="exact")
        snapshot=make_snapshot(course,request)
        result=solve_plan(snapshot.topic_weights,snapshot.request)
        items=select_questions(course,result,diagnostic.proficiency)
        st.session_state["plan"]={"result":result,"snapshot":snapshot,"items":items}
    except (ValueError,OSError) as error:
        st.session_state.pop("plan",None)
        st.error(f"could not make a plan - {error}")

if "plan" in st.session_state:
    saved=st.session_state["plan"]
    result=saved["result"]
    snapshot=saved["snapshot"]
    names={t.topic_id:t.name for t in course.topics}
    render_results({names[t]:v for t,v in snapshot.request.proficiency.items()}, {names[t]:v for t,v in result.allocations.items()})
    left,right=st.columns(2)
    left.metric("used time",f"{result.used_minutes} min")
    right.metric("unused time",f"{result.unused_minutes} min")
    st.caption(f"solver - {result.actual_solver}, mode - {result.execution_mode}, utility - {result.utility:.3f}")
    if result.used_minutes==0:
        st.info("no study blocks allocated - budget may be below 30 minutes, or all topic scores are 100%")
    questions={q.question_id:q for q in course.questions}
    sources={s.source_id:(s.label or s.filename or s.source_id) for s in course.sources}
    practice=[]
    for item in saved["items"]:
        q=questions[item.question_id]
        practice.append({"text":q.text,"topic":names[q.topic_id],"difficulty":q.difficulty,"source":sources[q.source_id],"page":q.page,"answer":q.answer,"reason":item.reason})
    render_practice_questions(practice)
    for topic,minutes in result.allocations.items():
        count=sum(questions[item.question_id].topic_id==topic for item in saved["items"])
        if minutes>0 and count<2:
            st.warning(f"{names[topic]} - only {count} unique practice questions available")
    st.download_button("download profile json",data=snapshot.model_dump_json(indent=2),file_name="student_profile.json",mime="application/json",key="profile_download")
    st.caption("save the fictional profile as runtime/student_profile.json for the separate qiskit script")
