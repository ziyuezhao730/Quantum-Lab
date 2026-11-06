"""interacting session selection - overlaps, prerequisites & deadlines"""
from datetime import datetime,timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
import subprocess

import numpy as np
from pydantic import BaseModel,Field,model_validator
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

from src.contracts import StudySnapshot
from src.optimizer.model import TOPICS


class Window(BaseModel):
    start: int = Field(ge=0,le=10080)
    end: int = Field(gt=0,le=10080)

    @model_validator(mode="after")
    def ordered(self):
        if self.end<=self.start:
            raise ValueError("window end must follow its start")
        return self


class Session(BaseModel):
    session_id: str
    topic_id: str
    kind: str
    start: int = Field(ge=0)
    minutes: int = Field(ge=15,le=45)
    requires: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid(self):
        if self.topic_id not in TOPICS or self.kind not in ("review","practice") or self.minutes%15 or self.start%15:
            raise ValueError("sessions need a topic, review/practice & 15-minute times")
        return self


class ScheduleSnapshot(BaseModel):
    schema_version: int = 3
    profile: StudySnapshot
    sessions: list[Session] = Field(min_length=1,max_length=18)
    windows: list[Window]
    deadlines: dict[str,int]

    @model_validator(mode="after")
    def valid(self):
        if self.schema_version!=3 or set(self.deadlines)!=set(TOPICS):
            raise ValueError("invalid scheduling version or topic deadlines")
        ids=[s.session_id for s in self.sessions]
        if len(ids)!=len(set(ids)):
            raise ValueError("session ids must be unique")
        for s in self.sessions:
            if any(r not in ids for r in s.requires):
                raise ValueError("unknown preparation session")
        return self


def make_options(profile,start_hour=9,end_hour=13,exam_days=None,prepare=True,days=3,session_minutes=45):
    if end_hour<=start_hour:
        raise ValueError("available time must end after it starts")
    exam_days=exam_days or {"T1":2,"T2":3,"T3":3}
    windows=[Window(start=d*1440+start_hour*60,end=d*1440+end_hour*60) for d in range(days)]
    sessions=[]
    for day in range(days):
        order=TOPICS[day%3:]+TOPICS[:day%3]
        for i,(kind,offset) in enumerate(zip(["review"]*3+["practice"]*3,[0,30,60,120,150,180])):
            topic=order[i%3]
            sessions.append(Session(session_id=f"d{day+1}-{topic}-{kind}",topic_id=topic,kind=kind,start=day*1440+start_hour*60+offset,minutes=session_minutes))
    if prepare:
        for s in sessions:
            if s.kind=="practice":
                s.requires=[r.session_id for r in sessions if r.topic_id==s.topic_id and r.kind=="review" and r.start+r.minutes+15<=s.start]
    return ScheduleSnapshot(profile=profile,sessions=sessions,windows=windows,deadlines={t:(exam_days[t]-1)*1440+end_hour*60 for t in TOPICS})


def session_values(snapshot):
    profile=snapshot.profile
    values=[]
    for s in snapshot.sessions:
        gap=profile.topic_weights[s.topic_id]*(1-profile.request.proficiency[s.topic_id])
        days=max(0,(snapshot.deadlines[s.topic_id]-s.start)/1440)
        urgency=1+1/(1+days)
        values.append(gap*urgency*(1.4 if s.kind=="practice" else 1.0)*(s.minutes/45))
    return np.array(values)


def landscape(snapshot):
    snapshot=ScheduleSnapshot.model_validate(snapshot)
    sessions=snapshot.sessions
    n=len(sessions)
    indices=np.arange(1<<n,dtype=np.uint32)
    bits=((indices[:,None]>>np.arange(n))&1).astype(np.int8)
    values=session_values(snapshot)
    utility=bits@values
    violations=np.zeros(len(indices),dtype=np.int16)
    ids={s.session_id:i for i,s in enumerate(sessions)}
    conflicts=[]
    for i,s in enumerate(sessions):
        allowed=any(w.start<=s.start and s.start+s.minutes<=w.end for w in snapshot.windows)
        if not allowed or s.start+s.minutes>snapshot.deadlines[s.topic_id]:
            violations+=bits[:,i]
        if s.requires:
            eligible=[ids[r] for r in s.requires if sessions[ids[r]].start+sessions[ids[r]].minutes+15<=s.start]
            satisfied=bits[:,eligible].any(axis=1) if eligible else np.zeros(len(bits),dtype=bool)
            violations+=bits[:,i]*(~satisfied)
        for j in range(i):
            other=sessions[j]
            if s.start<other.start+other.minutes+15 and other.start<s.start+s.minutes+15:
                violations+=bits[:,i]*bits[:,j]
                conflicts.append((j,i))
            if s.topic_id==other.topic_id and s.kind==other.kind:
                utility-=.2*min(values[i],values[j])*bits[:,i]*bits[:,j]
    study=bits@np.array([s.minutes for s in sessions],dtype=np.int16)
    used_days=np.zeros(len(indices),dtype=np.int16)
    for day in sorted({s.start//1440 for s in sessions}):
        used_days+=bits[:,[i for i,s in enumerate(sessions) if s.start//1440==day]].any(axis=1)
    breaks=15*(bits.sum(axis=1)-used_days)
    total=study+breaks
    over=(np.maximum(0,total-snapshot.profile.request.budget_minutes)+14)//15
    violations+=over*over
    valid=violations==0
    penalty=1+float(values.sum())
    energies=-utility+penalty*violations
    return {"indices":indices,"bits":bits,"utility":utility,"valid":valid,"study":study,"breaks":breaks,"total":total,"energies":energies,"values":values,"conflicts":conflicts,"penalty":penalty}


def selection_key(index,data):
    return (float(data["utility"][index]),-int(data["total"][index]),*data["bits"][index].tolist())


def package(snapshot,index,data,solver,elapsed=0):
    selected=[s for i,s in enumerate(snapshot.sessions) if data["bits"][index,i]]
    selected.sort(key=lambda s:(s.start,s.session_id))
    allocs={t:sum(s.minutes for s in selected if s.topic_id==t) for t in TOPICS}
    return {"allocations":allocs,"selected_sessions":[s.model_dump() for s in selected],"used_minutes":int(data["study"][index]),"break_minutes":int(data["breaks"][index]),"unused_minutes":snapshot.profile.request.budget_minutes-int(data["total"][index]),"utility":float(data["utility"][index]),"feasible":bool(data["valid"][index]),"actual_solver":solver,"execution_mode":"live","elapsed_ms":elapsed}


def exact_schedule(snapshot,data=None):
    start=perf_counter()
    data=landscape(snapshot) if data is None else data
    best=float(data["utility"][data["valid"]].max())
    tied=np.flatnonzero(data["valid"] & (np.abs(data["utility"]-best)<=1e-10))
    index=max(tied,key=lambda i:(-int(data["total"][i]),*data["bits"][i].tolist()))
    return package(snapshot,int(index),data,"exact",(perf_counter()-start)*1000)


def greedy_schedule(snapshot,data=None):
    start=perf_counter()
    data=landscape(snapshot) if data is None else data
    index=0
    while True:
        candidates=[index|(1<<i) for i in range(len(snapshot.sessions)) if not index&(1<<i)]
        candidates=[i for i in candidates if data["valid"][i] and data["utility"][i]>data["utility"][index]+1e-12]
        if not candidates:
            break
        index=max(candidates,key=lambda i:selection_key(i,data))
    return package(snapshot,index,data,"greedy",(perf_counter()-start)*1000)


def compare_schedule(snapshot,seed=7,evaluations=30,shots=1024):
    snapshot=ScheduleSnapshot.model_validate(snapshot)
    exact=exact_schedule(snapshot)
    start=perf_counter()
    data=landscape(snapshot)
    n=len(snapshot.sessions)
    energies=data["energies"]
    uniform_state=Statevector.from_label("+"*n)
    occupancy=min(.35,max(.02,snapshot.profile.request.budget_minutes/(float(np.mean([s.minutes for s in snapshot.sessions]))+15)/n))
    preparation=QuantumCircuit(n)
    preparation.ry(2*np.arcsin(np.sqrt(occupancy)),range(n))
    initial_state=Statevector.from_instruction(preparation)
    initial=np.random.default_rng(seed).uniform(0,np.pi,2)
    uniform_state.seed(seed)
    uniform_counts={key:int(val) for key,val in uniform_state.sample_counts(shots).items()}
    uniform_valid=[int(key,2) for key in uniform_counts if data["valid"][int(key,2)]]
    uniform_best=max(uniform_valid,key=lambda i:selection_key(i,data)) if uniform_valid else None
    uniform_rate=sum(count for key,count in uniform_counts.items() if data["valid"][int(key,2)])/shots
    trace=[]
    def state_at(angles):
        beta,gamma=angles
        phased=Statevector(initial_state.data*np.exp(-1j*gamma*energies/data["penalty"]))
        mixer=QuantumCircuit(n)
        mixer.rx(2*beta,range(n))
        return phased.evolve(mixer)
    def objective(angles):
        state=state_at(angles)
        energy=float(np.dot(state.probabilities(),energies))
        trace.append({"params":[float(a) for a in angles],"energy":energy})
        return energy
    opt=minimize(objective,initial,method="COBYLA",options={"maxiter":evaluations,"disp":False})
    state=state_at(opt.x)
    state.seed(seed)
    counts={key:int(val) for key,val in state.sample_counts(shots).items()}
    feasible=[int(key,2) for key in counts if data["valid"][int(key,2)]]
    best=max(feasible,key=lambda i:selection_key(i,data)) if feasible else None
    sampled=None if best is None else package(snapshot,best,data,"qaoa")
    rate=sum(count for key,count in counts.items() if data["valid"][int(key,2)])/shots
    elapsed=(perf_counter()-start)*1000
    root=Path(__file__).resolve().parents[2]
    commit=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
    dirty=bool(subprocess.run(["git","status","--porcelain"],cwd=root,capture_output=True,text=True,check=True).stdout.strip())
    return {"schema_version":3,"created_utc":datetime.now(timezone.utc).isoformat(),"code_commit":commit,"working_tree_dirty":dirty,"profile":snapshot.model_dump(mode="json"),"execution_mode":"live","reference":"https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm","versions":{name:version(name) for name in ("qiskit","numpy","scipy")},"exact":exact,"greedy":greedy_schedule(snapshot),"uniform":{"raw_best_utility":None if uniform_best is None else float(data["utility"][uniform_best]),"feasible_shot_rate":uniform_rate},"quantum":{"qubits":n,"p":1,"seed":seed,"shots":shots,"objective_evaluations":len(trace),"initial_params":initial.tolist(),"initial_selection_probability":occupancy,"cost_scale":data["penalty"],"parameter_order":["beta","gamma"],"params":opt.x.tolist(),"optimizer_success":bool(opt.success),"expected_energy":float(opt.fun),"best_sample":sampled,"raw_best_utility":None if sampled is None else sampled["utility"],"feasible_shot_rate":rate,"elapsed_ms":elapsed,"counts":counts,"trace":trace},"absolute_utility_gap":None if sampled is None else abs(exact["utility"]-sampled["utility"])}
