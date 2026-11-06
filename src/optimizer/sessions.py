"""schema 2 planner - 15-min blocks, breaks included"""
from math import fsum
from time import perf_counter

from src.contracts import PlanRequest, StudyRequest, StudySnapshot
from src.intelligence.pipeline import make_snapshot
from src.optimizer.model import TOPICS, topic_priority


def make_study_snapshot(course, proficiency, budget):
    # reuse reviewed count weights, without changing the old export contract
    base=make_snapshot(course,PlanRequest(budget_minutes=0,proficiency=proficiency,requested_solver="exact"))
    return StudySnapshot(schema_version=2,profile_source="diagnostic",topic_weights=base.topic_weights,request=StudyRequest(budget_minutes=budget,proficiency=proficiency,requested_solver="exact"))


def study_capacity(request):
    slots=request.budget_minutes//15
    # three work slots before each break, no break after the final work slot
    return max((n for n in range(slots+1) if n+max(0,(n-1)//3)<=slots),default=0)


def priorities(snapshot):
    return {t:topic_priority(snapshot.topic_weights[t],snapshot.request.proficiency[t]) for t in TOPICS}


def allocation_utility(allocs, vals):
    # nth 15-min block gets a/n, giving diminishing returns beyond the first hour
    return fsum(vals[t]/n for t in TOPICS for n in range(1,allocs[t]//15+1))


def timeline(allocs):
    events=[]
    elapsed=0
    work=0
    previous=None
    remaining={t:allocs[t]//15 for t in TOPICS}
    while sum(remaining.values()):
        if work==3:
            events.append({"kind":"break","topic_id":None,"start_minutes":elapsed,"duration_minutes":15})
            elapsed+=15
            work=0
        # keep a topic together for one focus period, rotate when another needs time
        choices=[t for t in TOPICS if remaining[t] and t!=previous]
        if not choices:
            choices=[t for t in TOPICS if remaining[t]]
        topic=max(choices,key=lambda t:(remaining[t],-TOPICS.index(t)))
        count=min(3-work,remaining[topic])
        for _ in range(count):
            events.append({"kind":"study","topic_id":topic,"start_minutes":elapsed,"duration_minutes":15})
            elapsed+=15
        remaining[topic]-=count
        work+=count
        previous=topic
    return events


def pack_plan(snapshot, allocs, solver="exact", elapsed_ms=0.0):
    events=timeline(allocs)
    used=sum(allocs.values())
    breaks=sum(e["duration_minutes"] for e in events if e["kind"]=="break")
    feasible=set(allocs)==set(TOPICS) and all(type(v) is int and v>=0 and v%15==0 for v in allocs.values()) and used+breaks<=snapshot.request.budget_minutes
    return {"allocations":allocs,"used_minutes":used,"break_minutes":breaks,"unused_minutes":snapshot.request.budget_minutes-used-breaks,"utility":allocation_utility(allocs,priorities(snapshot)),"timeline":events,"feasible":feasible,"actual_solver":solver,"execution_mode":"live","elapsed_ms":elapsed_ms}


def solve_session(snapshot):
    snapshot=StudySnapshot.model_validate(snapshot)
    start=perf_counter()
    vals=priorities(snapshot)
    allocs=dict.fromkeys(TOPICS,0)
    for _ in range(study_capacity(snapshot.request)):
        gains={t:vals[t]/(allocs[t]//15+1) for t in TOPICS}
        best=max(gains.values())
        if best<=1e-12:
            break
        topic=next(t for t in TOPICS if abs(gains[t]-best)<=1e-12)
        allocs[topic]+=15
    return pack_plan(snapshot,allocs,elapsed_ms=(perf_counter()-start)*1000)
