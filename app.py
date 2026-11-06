"""study dashboard - schema 2, short diagnostic & break-aware sessions"""
import json
from pathlib import Path
from types import SimpleNamespace

import streamlit as st

from src.intelligence.pipeline import load_course
from src.intelligence.rank import select_questions
from src.optimizer.sessions import make_study_snapshot,solve_session
from src.optimizer.session_quantum import compare_session
from src.ui.study_inputs import clear_plan,open_diagnostic,diagnostic_dialog
from src.ui.dashboard import theme,duration,render_plan,render_practice

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="ExamAce · your study desk",page_icon="📖",layout="wide")
theme()
try:
    course=load_course(ROOT/"data/demo/course.json")
except (ValueError,OSError) as error:
    st.error(f"course data could not be loaded - {error}")
    st.stop()

if "diag_seen" not in st.session_state:
    st.session_state.update(diag_seen=True,diag_open=True,diag_step=0,diag_answers={})

with st.sidebar:
    st.markdown("## examace")
    st.caption("CALCULUS · STUDY DESK")
    st.divider()
    st.markdown("#### Make time for it")
    hours=st.number_input("Hours available",min_value=0,max_value=24,value=2,step=1,key="study_hours",on_change=clear_plan)
    mins=st.selectbox("Extra minutes",options=[0] if hours==24 else [0,15,30,45],key="study_mins",on_change=clear_plan)
    budget=hours*60+mins
    st.caption(f"{duration(budget)} total · breaks included")
    st.caption("15-minute blocks. Work for up to 45 minutes, then take 15 minutes away.")
    st.divider()
    if st.button("Retake diagnostic",key="retake",use_container_width=True):
        open_diagnostic()
        st.rerun()
    if "proficiency" in st.session_state:
        st.caption("Initial topic score from two questions")
        for topic in course.topics:
            st.write(f"{topic.name} · {st.session_state['proficiency'][topic.topic_id]:.0%}")

st.markdown('<div class="eyebrow">calculus / study session</div>',unsafe_allow_html=True)
st.title("Your next study session")
st.write("Choose your time. Focus where you need it. Leave room to breathe.")
if "proficiency" not in st.session_state:
    st.info("Start with six quick questions so the plan reflects your starting point.")
    if st.button("Take the diagnostic",key="start_diagnostic",type="primary"):
        open_diagnostic()
        st.rerun()
else:
    if st.button("Build my plan",key="build_plan",type="primary"):
        snapshot=make_study_snapshot(course,st.session_state["proficiency"],budget)
        result=solve_session(snapshot)
        items=select_questions(course,SimpleNamespace(allocations=result["allocations"],feasible=result["feasible"]),snapshot.request.proficiency)
        st.session_state["study_plan"]={"snapshot":snapshot,"result":result,"items":items}
        st.session_state.pop("experiment",None)

plan_tab,practice_tab,experiment_tab=st.tabs(["Study plan","Practice","Quantum lab"])
saved=st.session_state.get("study_plan")
with plan_tab:
    if saved:
        render_plan(saved["result"],{t.topic_id:t.name for t in course.topics})
        st.download_button("Save session profile",data=saved["snapshot"].model_dump_json(indent=2),file_name="student_profile.json",mime="application/json",key="session_download")
        with st.expander("How the allocation works"):
            st.write("Weighted gaps in topic scores set the priority. Each additional 15 minutes of study adds less value. The next block goes to the topic with the highest remaining priority.")
    else:
        st.caption("Your plan will appear here after the diagnostic & a session budget.")
with practice_tab:
    if saved:
        render_practice(course,saved["items"],saved["result"])
    else:
        st.info("Build a session to see practice for its allocated topics.")
with experiment_tab:
    st.markdown("### A different solver")
    st.write("Compare your plan with a local QAOA simulation as an experiment.")
    if saved and st.button("Run a local comparison",key="run_quantum"):
        with st.spinner("Simulating your session…"):
            st.session_state["experiment"]=compare_session(saved["snapshot"])
    report=st.session_state.get("experiment")
    if report:
        quantum=report["quantum"]
        a,b,c=st.columns(3)
        a.metric("Planner score",f"{report['exact']['utility']:.3f}")
        b.metric("QAOA score","no feasible sample" if quantum['raw_best_utility'] is None else f"{quantum['raw_best_utility']:.3f}")
        c.metric("Feasible samples",f"{quantum['feasible_shot_rate']:.1%}")
        st.caption(f"{quantum['qubits']} qubits · {quantum['shots']:,} samples")
        if quantum["best_sample"]:
            for topic in course.topics:
                st.write(f"**{topic.name}** · {duration(quantum['best_sample']['allocations'][topic.topic_id])}")
        else:
            st.warning("The simulation did not find a plan that fits. Try another comparison.")
        st.download_button("Save comparison",data=json.dumps(report,indent=2),file_name="session_comparison.json",mime="application/json",key="comparison_download")

if st.session_state.get("diag_open",False):
    diagnostic_dialog(course)
