"""r3 self-checks"""
from math import isclose

import pytest
from qiskit.quantum_info import Statevector

from src.contracts import PlanRequest
from src.optimizer.model import build_binary_model, binary_to_ising, binary_energy
from src.optimizer.quantum_demo import cost_operator, select_sample

weights = {"T1": 1.0, "T2": 1.0, "T3": 1.0}


@pytest.mark.parametrize("budget,bits", [
    (0, [0]*9),
    (90, [0,0,1,1,1,0,0,0,0]),
    (180, [1,1,1,1,1,1,0,0,0]),
    (90, [0,1,1,0,1,0,0,0,0]),
])
def test_operator_energy(budget, bits):
    request = PlanRequest(budget_minutes=budget, proficiency={"T1": .8, "T2": .2, "T3": .4}, requested_solver="qaoa")
    model = binary_to_ising(build_binary_model(weights, request))
    op, offset = cost_operator(model)
    state = Statevector.from_label("".join(str(bit) for bit in reversed(bits)))
    energy = float(state.expectation_value(op).real + offset)
    assert isclose(energy, binary_energy(bits, weights, request), abs_tol=1e-8)


def test_sample_ties_and_feasibility():
    request = PlanRequest(budget_minutes=30, proficiency=dict.fromkeys(weights, 0.0), requested_solver="qaoa")
    # two valid equal-utility plans, second block without first is invalid
    counts = {"000000100": 2, "000000001": 1, "000000010": 7}
    best, bits, rate = select_sample(counts, weights, request)
    assert best["allocations"] == {"T1": 30, "T2": 0, "T3": 0}
    assert bits == [1,0,0,0,0,0,0,0,0]
    assert rate == .3


def test_no_feasible_sample():
    request = PlanRequest(budget_minutes=90, proficiency=dict.fromkeys(weights, 0.0), requested_solver="qaoa")
    best, bits, rate = select_sample({"000000000": 1024}, weights, request)
    assert best is None
    assert bits is None
    assert rate == 0


def test_fewer_blocks_tie():
    request = PlanRequest(budget_minutes=30, proficiency=dict.fromkeys(weights, 1.0), requested_solver="qaoa")
    best, _, _ = select_sample({"000000001": 3, "001000000": 1}, weights, request)
    assert best["used_minutes"] == 0



def test_saved_run():
    import json
    from pathlib import Path
    from src.intelligence.validate import validate_snapshot
    from src.optimizer.classical import solve_plan
    from src.optimizer.quantum_demo import load_profile

    root = Path(__file__).resolve().parents[2]
    report = json.loads((root / "evidence/risi/qaoa_run.json").read_text())
    snapshot = validate_snapshot(report["profile"])
    quantum = report["quantum"]
    assert report["execution_mode"] == "live"
    assert quantum["qubits"] == 9
    assert quantum["p"] == 1
    assert quantum["seed"] == 7
    assert quantum["shots"] == sum(quantum["counts"].values()) == 1024
    assert 0 < quantum["objective_evaluations"] == len(quantum["trace"]) <= 30
    exact = solve_plan(snapshot.topic_weights, snapshot.request.model_copy(update={"requested_solver": "exact"}))
    assert exact.allocations == report["exact"]["allocations"]
    assert isclose(exact.utility, report["exact"]["utility"])
    best, bits, rate = select_sample(quantum["counts"], snapshot.topic_weights, snapshot.request)
    assert best is not None
    assert best == quantum["best_sample"]
    assert bits == quantum["best_bits"]
    assert rate == quantum["feasible_shot_rate"]
    assert isclose(report["absolute_utility_gap"], abs(exact.utility - best["utility"]))
