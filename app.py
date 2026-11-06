"""study dashboard - schema 2, short diagnostic & break-aware sessions"""
import json
from pathlib import Path
from types import SimpleNamespace

import streamlit as st

from src.intelligence.pipeline import load_course
from src.intelligence.rank import select_questions
from src.optimizer.sessions import make_study_snapshot,solve_session
from src.optimizer.scheduler import make_options,exact_schedule,compare_schedule
from src.ui.study_inputs import clear_plan,open_diagnostic,diagnostic_dialog
from src.ui.dashboard import theme,duration,render_schedule,render_practice

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
    st.caption("15-minute breaks between sessions")
    with st.expander("Availability & exams"):
        session_minutes=st.selectbox("Focus length",[15,30,45],index=2,format_func=lambda m:f"{m} minutes",key="session_minutes",on_change=clear_plan)
        days=st.selectbox("Planning days",[1,2,3],index=2,key="planning_days",on_change=clear_plan)
        start_hour=st.selectbox("Available from",list(range(6,22)),index=3,format_func=lambda h:f"{h:02d}:00",key="available_start",on_change=clear_plan)
        end_hour=st.selectbox("Available until",list(range(7,25)),index=6,format_func=lambda h:f"{h:02d}:00",key="available_end",on_change=clear_plan)
        exam_days={}
        for topic in course.topics:
            exam_days[topic.topic_id]=st.selectbox(f"{topic.name} exam",[1,2,3],index=1 if topic.topic_id=="T1" else 2,format_func=lambda d:f"Day {d} · {end_hour:02d}:00",key=f"exam_{topic.topic_id}",on_change=clear_plan)
        prepare=st.checkbox("Review before practice",value=True,key="prepare",on_change=clear_plan)
    st.divider()
    if st.button("Retake diagnostic",key="retake",use_container_width=True):
        open_diagnostic()
        st.rerun()
    if "proficiency" in st.session_state:
        st.caption("Initial topic score from two questions")
        for topic in course.topics:
            st.write(f"{topic.name} · {st.session_state['proficiency'][topic.topic_id]:.0%}")

st.markdown('<div class="eyebrow">calculus / study session</div>',unsafe_allow_html=True)
st.title("Your exam-week plan")
st.write("Choose your availability. Fit study around your exams.")
if "proficiency" not in st.session_state:
    st.info("Start with six quick questions so the plan reflects your starting point.")
    if st.button("Take the diagnostic",key="start_diagnostic",type="primary"):
        open_diagnostic()
        st.rerun()
else:
    if st.button("Build my plan",key="build_plan",type="primary"):
        try:
            profile=make_study_snapshot(course,st.session_state["proficiency"],budget)
            snapshot=make_options(profile,start_hour,end_hour,exam_days,prepare,days,session_minutes)
            result=exact_schedule(snapshot)
            items=select_questions(course,SimpleNamespace(allocations=result["allocations"],feasible=result["feasible"]),profile.request.proficiency)
            st.session_state["study_plan"]={"snapshot":snapshot,"result":result,"items":items}
            st.session_state.pop("experiment",None)
        except ValueError as error:
            st.error(str(error))

plan_tab,practice_tab,experiment_tab=st.tabs(["Study plan","Practice","Quantum lab"])
saved=st.session_state.get("study_plan")
with plan_tab:
    if saved:
        render_schedule(saved["result"],{t.topic_id:t.name for t in course.topics},saved["snapshot"])
        st.download_button("Save session profile",data=saved["snapshot"].model_dump_json(indent=2),file_name="student_profile.json",mime="application/json",key="session_download")
        with st.expander("How the allocation works"):
            st.write("Topic scores & exam dates set the priorities. The planner picks a combination that fits your availability. It keeps review ahead of practice & leaves space for breaks.")
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
            st.session_state["experiment"]=compare_schedule(saved["snapshot"])
    report=st.session_state.get("experiment")
    if report:
        quantum=report["quantum"]
        a,b,c=st.columns(3)
        a.metric("Exact score",f"{report['exact']['utility']:.3f}")
        b.metric("Greedy score",f"{report['greedy']['utility']:.3f}")
        c.metric("QAOA score","no feasible sample" if quantum['raw_best_utility'] is None else f"{quantum['raw_best_utility']:.3f}")
        st.caption(f"Feasible samples · {quantum['feasible_shot_rate']:.1%}")
        st.caption(f"{quantum['qubits']} qubits · {quantum['shots']:,} samples")
        if quantum["best_sample"]:
            for topic in course.topics:
                st.write(f"**{topic.name}** · {duration(quantum['best_sample']['allocations'][topic.topic_id])}")
        else:
            st.warning("The simulation did not find a plan that fits. Try another comparison.")
        st.download_button("Save comparison",data=json.dumps(report,indent=2),file_name="session_comparison.json",mime="application/json",key="comparison_download")

    benchmark_path=ROOT/"evidence/risi/scheduler_benchmark.json"
    if benchmark_path.exists():
        with st.expander("Saved example runs"):
            benchmark=json.loads(benchmark_path.read_text())
            rows=[{"Case":r["case"].replace("_"," "),"Options":r["choices"],"Seed":r["seed"],"Exact":round(r["exact"],3),"Greedy":round(r["greedy"],3),"QAOA":None if r["qaoa"] is None else round(r["qaoa"],3),"Feasible samples":f"{r['feasible_rate']:.1%}"} for r in benchmark["results"]]
            st.dataframe(rows,hide_index=True,use_container_width=True)

if st.session_state.get("diag_open",False):
    diagnostic_dialog(course)
