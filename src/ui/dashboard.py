"""quiet session dashboard, plan & practice views"""
import html
import streamlit as st


def theme():
    st.markdown("""<style>
    .stApp {background:#f6f5f0;}
    .block-container {max-width:1120px;padding-top:2.2rem;padding-bottom:3rem;}
    h1,h2,h3 {letter-spacing:-.035em;color:#26382e;}
    h1 {font-family:Georgia,serif;font-weight:500!important;font-size:2.8rem!important;}
    h2 {font-size:1.6rem!important;}
    [data-testid="stMetric"] {background:white;border:1px solid #e0e6df;border-radius:12px;padding:16px;}
    [data-testid="stMetricValue"] {font-size:1.8rem;}
    [data-baseweb="tab-list"] {gap:24px;background:transparent;border-bottom:1px solid #d9e1d9;}
    [data-baseweb="tab"] {background:transparent;font-weight:600;padding:14px 0;}
    [data-testid="stSidebar"] {border-right:1px solid #e0e6df;background:#eeefe8;}
    .eyebrow {font-size:.72rem;text-transform:uppercase;letter-spacing:.15em;color:#71806c;margin-bottom:8px;}
    .session-card {border-left:3px solid #698c70;background:white;padding:12px 17px;margin:8px 0;border-radius:0 10px 10px 0;}
    .pause-card {border-left-color:#c4b68c;background:#efeee6;}
    .session-time {font-size:.75rem;color:#73806e;margin-bottom:3px;}
    .session-topic {font-size:1rem;font-weight:600;color:#26382e;}
    .session-note {font-size:.8rem;color:#71806c;margin-top:3px;}
    @media(max-width:700px){h1{font-size:2.1rem!important;}.block-container{padding-top:1rem;}[data-baseweb="tab-list"]{gap:16px;}}
    </style>""",unsafe_allow_html=True)


def duration(minutes):
    hours,mins=divmod(minutes,60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins}m"


def clock(minutes):
    return f"{minutes//60}:{minutes%60:02d}"


def render_plan(plan,names):
    a,b,c=st.columns(3)
    a.metric("Focused study",duration(plan["used_minutes"]))
    b.metric("Breaks",duration(plan["break_minutes"]))
    c.metric("Time left",duration(plan["unused_minutes"]))
    st.markdown("### Your focus areas")
    for topic,minutes in sorted(plan["allocations"].items(),key=lambda pair:(-pair[1],pair[0])):
        if minutes:
            st.write(f"**{names[topic]}** · {duration(minutes)}")
            st.progress(minutes/max(plan["used_minutes"],1))
    if not plan["used_minutes"]:
        st.info("No study blocks allocated. Try a longer budget or retake the diagnostic if these scores do not reflect where you need practice.")
        return
    st.markdown("### A session you can follow")
    st.caption("times are elapsed from your start · a 15-minute break after each 45 minutes of work")
    grouped=[]
    for event in plan["timeline"]:
        if grouped and event["kind"]=="study" and grouped[-1]["kind"]=="study" and event["topic_id"]==grouped[-1]["topic_id"]:
            grouped[-1]["duration_minutes"]+=15
        else:
            grouped.append(event.copy())
    for event in grouped:
        start=event["start_minutes"]
        end=start+event["duration_minutes"]
        pause=event["kind"]=="break"
        title="Take a break" if pause else names[event["topic_id"]]
        note="step away, stretch, get some water" if pause else "review the topic, then work through its practice questions"
        st.markdown(f'<div class="session-card {"pause-card" if pause else ""}"><div class="session-time">{clock(start)} — {clock(end)}</div><div class="session-topic">{html.escape(title)}</div><div class="session-note">{note}</div></div>',unsafe_allow_html=True)


def render_practice(course,items,plan):
    questions={q.question_id:q for q in course.questions}
    sources={s.source_id:(s.label or s.filename or s.source_id) for s in course.sources}
    names={t.topic_id:t.name for t in course.topics}
    st.markdown("### PRACTICE")
    st.caption("practice with a reviewed question bank.")
    if not items:
        st.info("Build a plan with allocated study time to see targeted practice.")
    for item in items:
        q=questions[item.question_id]
        with st.container(border=True):
            st.caption(f"{names[q.topic_id].upper()} · LEVEL {q.difficulty}")
            st.markdown(f"#### {q.text}")
            st.caption(f"{sources[q.source_id]} · page {q.page}")
            with st.expander("Why this question?"):
                st.write(item.reason)
            if q.answer is None:
                st.caption("answer unavailable")
            else:
                with st.expander("Check your answer"):
                    st.write(q.answer)
    for topic,minutes in plan["allocations"].items():
        count=sum(questions[i.question_id].topic_id==topic for i in items)
        if minutes and count<2:
            st.warning(f"{names[topic]} - only {count} unique practice questions available")
