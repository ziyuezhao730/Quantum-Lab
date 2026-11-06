"""compact p=1 qaoa for schema 2 study sessions"""
from math import ceil,log2
import subprocess
from pathlib import Path
from datetime import datetime,timezone
from importlib.metadata import version
from time import perf_counter

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

from src.contracts import StudySnapshot
from src.optimizer.model import TOPICS
from src.optimizer.sessions import study_capacity,priorities,pack_plan,solve_session


def energy_table(snapshot):
    capacity=study_capacity(snapshot.request)
    vals=priorities(snapshot)
    if not any(v>1e-12 for v in vals.values()):
        capacity=0
    width=max(1,ceil(log2(capacity+1)))
    harmonics=np.concatenate(([0.0],np.cumsum(1/np.arange(1,capacity+1))))
    penalty=1+sum(vals.values())*harmonics[-1]
    indices=np.arange(1<<(2*width))
    first=indices&((1<<width)-1)
    second=indices>>width
    third=capacity-first-second
    valid=third>=0
    energies=np.full(len(indices),penalty)
    energies[valid]=-(vals["T1"]*harmonics[first[valid]]+vals["T2"]*harmonics[second[valid]]+vals["T3"]*harmonics[third[valid]])
    return energies,valid,width,capacity


def decode_counts(counts,snapshot,width,capacity):
    best=None
    best_bits=None
    feasible_shots=0
    for bitstr,count in counts.items():
        index=int(bitstr,2)
        first=index&((1<<width)-1)
        second=index>>width
        third=capacity-first-second
        if third<0:
            continue
        allocs=dict(zip(TOPICS,[15*first,15*second,15*third]))
        plan=pack_plan(snapshot,allocs,solver="qaoa")
        if not plan["feasible"]:
            continue
        feasible_shots+=count
        key=(plan["utility"],-plan["used_minutes"],*allocs.values())
        if best is None or key>(best["utility"],-best["used_minutes"],*best["allocations"].values()):
            best=plan
            best_bits=bitstr
    return best,best_bits,feasible_shots/sum(counts.values())


def compare_session(snapshot):
    snapshot=StudySnapshot.model_validate(snapshot)
    exact=solve_session(snapshot)
    start=perf_counter()
    energies,valid,width,capacity=energy_table(snapshot)
    qubits=2*width
    initial_state=Statevector.from_label("+"*qubits)
    rng=np.random.default_rng(7)
    initial=rng.uniform(0,np.pi,2)
    trace=[]

    def state_at(angles):
        beta,gamma=angles
        # diagonal cost changes phases, default x mixer turns relative phase into probabilities
        phased=Statevector(initial_state.data*np.exp(-1j*gamma*energies))
        mixer=QuantumCircuit(qubits)
        mixer.rx(2*beta,range(qubits))
        return phased.evolve(mixer)

    def objective(angles):
        state=state_at(angles)
        energy=float(np.dot(state.probabilities(),energies))
        trace.append({"params":[float(a) for a in angles],"energy":energy})
        return energy

    result=minimize(objective,initial,method="COBYLA",options={"maxiter":30,"disp":False})
    state=state_at(result.x)
    state.seed(7)
    counts={key:int(val) for key,val in state.sample_counts(1024).items()}
    best,bits,rate=decode_counts(counts,snapshot,width,capacity)
    elapsed=(perf_counter()-start)*1000
    root=Path(__file__).resolve().parents[2]
    commit=subprocess.run(["git","rev-parse","HEAD"],cwd=root,check=True,capture_output=True,text=True).stdout.strip()
    dirty=bool(subprocess.run(["git","status","--porcelain"],cwd=root,check=True,capture_output=True,text=True).stdout.strip())
    return {"created_utc":datetime.now(timezone.utc).isoformat(),"code_commit":commit,"working_tree_dirty":dirty,"reference":"https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm","versions":{name:version(name) for name in ("qiskit","numpy","scipy","pydantic")},"schema_version":2,"profile":snapshot.model_dump(mode="json"),"execution_mode":"live","model":"two count registers, third topic is remaining study capacity; diagonal cost, default x mixer","exact":exact,"quantum":{"actual_solver":"qaoa","execution_mode":"live","qubits":qubits,"bits_per_register":width,"study_capacity_blocks":capacity,"p":1,"shots":1024,"seed":7,"parameter_order":["beta","gamma"],"initial_params":initial.tolist(),"params":result.x.tolist(),"objective_evaluations":len(trace),"expected_energy":float(result.fun),"optimizer_success":bool(result.success),"best_sample":best,"best_bits":bits,"raw_best_utility":None if best is None else best["utility"],"feasible_shot_rate":rate,"elapsed_ms":elapsed,"trace":trace,"counts":counts},"absolute_utility_gap":None if best is None else abs(exact["utility"]-best["utility"]),"limitations":["one local ideal simulation, no hardware timing or quantum advantage claim","harmonic study-priority heuristic, not predicted learning"]}
