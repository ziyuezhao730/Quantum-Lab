from itertools import product
from math import isclose

import numpy as np
import pytest

from src.contracts import StudyRequest,StudySnapshot
from src.optimizer.sessions import solve_session,study_capacity,allocation_utility,priorities
from src.optimizer.session_quantum import energy_table,decode_counts,compare_session


def snapshot(budget,scores=None):
    return StudySnapshot(schema_version=2,profile_source="diagnostic",request=StudyRequest(budget_minutes=budget,proficiency=scores or {"T1":1.,"T2":0.,"T3":.5},requested_solver="exact"),topic_weights={"T1":1.,"T2":1.,"T3":1.})


@pytest.mark.parametrize("budget",[0,14,15,44,45,59,60,75,180,600,1440])
def test_breaks_budget_and_timeline(budget):
    profile=snapshot(budget)
    plan=solve_session(profile)
    assert plan["feasible"]
    assert plan["used_minutes"]+plan["break_minutes"]+plan["unused_minutes"]==budget
    assert plan["allocations"]["T1"]==0
    assert all(v%15==0 for v in plan["allocations"].values())
    assert all(event["start_minutes"]==15*i for i,event in enumerate(plan["timeline"]))
    assert not plan["timeline"] or plan["timeline"][-1]["kind"]=="study"
    work=0
    for event in plan["timeline"]:
        if event["kind"]=="break":
            assert work==3
            work=0
        else:
            work+=1
            assert work<=3


def test_ten_hours_includes_breaks():
    plan=solve_session(snapshot(600))
    assert plan["used_minutes"]==450
    assert plan["break_minutes"]==135
    assert plan["unused_minutes"]==15


@pytest.mark.parametrize("budget",[15,45,75,120,180])
def test_matches_independent_enumeration(budget):
    profile=snapshot(budget,{"T1":.8,"T2":.2,"T3":.4})
    result=solve_session(profile)
    capacity=study_capacity(profile.request)
    vals=priorities(profile)
    candidates=[]
    for counts in product(range(capacity+1),repeat=3):
        if sum(counts)>capacity:
            continue
        allocs=dict(zip(("T1","T2","T3"),(15*n for n in counts)))
        # explicit reference, independent of the production utility helper
        utility=sum(profile.topic_weights[t]*(1-profile.request.proficiency[t])*sum(1/k for k in range(1,allocs[t]//15+1)) for t in allocs)
        candidates.append((utility,-sum(counts),*counts))
    oracle=max(candidates)
    assert isclose(result["utility"],oracle[0],abs_tol=1e-12)
    assert tuple(v//15 for v in result["allocations"].values())==oracle[2:]


def test_zero_benefit_and_roundtrip():
    profile=snapshot(600,dict.fromkeys(("T1","T2","T3"),1.))
    assert solve_session(profile)["used_minutes"]==0
    assert StudySnapshot.model_validate_json(profile.model_dump_json())==profile


@pytest.mark.parametrize("budget",[15,180,600,1440])
def test_compact_energy_matches_classical(budget):
    profile=snapshot(budget)
    energies,valid,width,capacity=energy_table(profile)
    index=int(np.argmin(energies))
    assert valid[index]
    best,bits,rate=decode_counts({format(index,f"0{2*width}b"):1024},profile,width,capacity)
    assert best["feasible"] and rate==1
    assert isclose(best["utility"],solve_session(profile)["utility"],abs_tol=1e-12)
    assert isclose(energies[index],-best["utility"],abs_tol=1e-12)
    assert 2*width<=14


def test_real_ten_hour_quantum_attempt():
    report=compare_session(snapshot(600))
    q=report["quantum"]
    assert q["qubits"]==10
    assert 0<q["objective_evaluations"]<=30
    assert sum(q["counts"].values())==1024
    assert q["best_sample"] is not None
    assert q["best_sample"]["feasible"]
    assert q["best_sample"]["used_minutes"]+q["best_sample"]["break_minutes"]<=600



def test_cli_loads_versioned_profile(tmp_path):
    from src.optimizer.quantum_demo import load_profile,compare
    profile=snapshot(600)
    path=tmp_path/"profile.json"
    path.write_text(profile.model_dump_json())
    restored=load_profile(path)
    assert isinstance(restored,StudySnapshot)
    assert restored==profile
    report=compare(restored)
    assert report["schema_version"]==2
    assert report["profile"]["request"]["budget_minutes"]==600



def test_focus_periods_rotate_when_both_topics_need_time():
    plan=solve_session(snapshot(600))
    work=[e["topic_id"] for e in plan["timeline"] if e["kind"]=="study"]
    assert len(set(work[:6]))==2
    for topic in ("T1","T2","T3"):
        assert 15*work.count(topic)==plan["allocations"][topic]
