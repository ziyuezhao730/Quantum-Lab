"""bounded qaoa simulation, separate from the app"""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

from src.intelligence.validate import validate_snapshot
from src.optimizer.classical import solve_plan
from src.optimizer.model import (
    BIT_ORDER, TOPICS, binary_to_ising, build_binary_model,
    decode_bits, qiskit_bitstring_to_bits,
)

SEED = 7
SHOTS = 1024
MAX_EVALS = 30
REF = "https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm"
ROOT = Path(__file__).resolve().parents[2]


def load_profile(path):
    """load & validate the exported snapshot"""
    return validate_snapshot(json.loads(Path(path).read_text()))


def cost_operator(model):
    """make z & zz terms, return offset separately"""
    terms = []
    for j, coeff in enumerate(model["linear"]):
        terms.append(("Z", [j], coeff))
    for (j, k), coeff in model["quadratic"].items():
        terms.append(("ZZ", [j, k], coeff))
    op = SparsePauliOp.from_sparse_list(terms, num_qubits=9).simplify()
    return op, model["offset"]


def select_sample(counts, weights, request):
    """pick best feasible sample, same tie rule as exact"""
    best = None
    best_bits = None
    feasible_shots = 0
    for bitstr, count in counts.items():
        bits = qiskit_bitstring_to_bits(bitstr)
        plan = decode_bits(bits, weights, request)
        if not plan["feasible"]:
            continue
        feasible_shots += count
        mins = tuple(plan["allocations"][t] for t in TOPICS)
        tie = (-plan["used_minutes"], *mins)
        if best is not None:
            diff = plan["utility"] - best["utility"]
            best_mins = tuple(best["allocations"][t] for t in TOPICS)
            best_tie = (-best["used_minutes"], *best_mins)
            if diff < -1e-12 or (abs(diff) <= 1e-12 and tie <= best_tie):
                continue
        best = plan
        best_bits = bits
    return best, best_bits, feasible_shots / sum(counts.values())


def run_qaoa(snapshot):
    """one start, 30 evals max, 1024 final samples"""
    snapshot = validate_snapshot(snapshot)
    start = perf_counter()
    request = snapshot.request.model_copy(update={"requested_solver": "qaoa"})
    binary = build_binary_model(snapshot.topic_weights, request)
    ising = binary_to_ising(binary)
    op, offset = cost_operator(ising)
    circuit = QAOAAnsatz(cost_operator=op, reps=1, flatten=True)
    params = tuple(circuit.parameters)
    rng = np.random.default_rng(SEED)
    initial = rng.uniform(0, np.pi, len(params))
    trace = []

    def objective(angles):
        bound = circuit.assign_parameters(dict(zip(params, angles)))
        state = Statevector.from_instruction(bound)
        energy = float(state.expectation_value(op).real + offset)
        trace.append({"params": [float(a) for a in angles], "energy": energy})
        return energy

    result = minimize(
        objective, initial, method="COBYLA",
        options={"maxiter": MAX_EVALS, "disp": False},
    )
    bound = circuit.assign_parameters(dict(zip(params, result.x)))
    state = Statevector.from_instruction(bound)
    state.seed(SEED)
    counts = {key: int(val) for key, val in state.sample_counts(SHOTS).items()}
    best, bits, rate = select_sample(counts, snapshot.topic_weights, request)
    elapsed = (perf_counter() - start) * 1000
    return {
        "actual_solver": "qaoa",
        "execution_mode": "live",
        "backend": "local statevector simulation",
        "qubits": circuit.num_qubits,
        "p": 1,
        "shots": SHOTS,
        "seed": SEED,
        "objective_evaluations": len(trace),
        "initial_params": initial.tolist(),
        "parameter_order": [str(param) for param in params],
        "params": result.x.tolist(),
        "expected_energy": float(result.fun),
        "offset": offset,
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "best_sample": best,
        "best_bits": bits,
        "raw_best_utility": None if best is None else best["utility"],
        "feasible_shot_rate": rate,
        "elapsed_ms": elapsed,
        "status": "failed" if best is None else "feasible sample found",
        "warnings": ["no feasible sample"] if best is None else [],
        "trace": trace,
        "counts": counts,
    }


def compare(snapshot):
    """same profile for exact & qaoa, save original inputs"""
    snapshot = validate_snapshot(snapshot)
    exact_request = snapshot.request.model_copy(update={"requested_solver": "exact"})
    exact = solve_plan(snapshot.topic_weights, exact_request)
    quantum = run_qaoa(snapshot)
    best_util = quantum["raw_best_utility"]
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    dirty = bool(subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT,
        check=True, capture_output=True, text=True,
    ).stdout.strip())
    return {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "live",
        "profile": snapshot.model_dump(mode="json"),
        "code_commit": commit,
        "working_tree_dirty": dirty,
        "reference": REF,
        "adaptation": "study allocation cost, p=1, local statevector, bounded cobyla",
        "bit_order": list(BIT_ORDER),
        "versions": {name: version(name) for name in ("qiskit", "numpy", "scipy", "pydantic")},
        "exact": exact.model_dump(mode="json"),
        "quantum": quantum,
        "absolute_utility_gap": None if best_util is None else abs(exact.utility - best_util),
        "limitations": [
            "one fictional profile, local simulation",
            "no hardware timing, quantum advantage or learning gain claim",
            "uncommitted code recorded separately from code_commit" if dirty else "committed code",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="compare exact & qaoa on an exported profile")
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "runtime/quantum_comparison.json")
    args = parser.parse_args()
    try:
        report = compare(load_profile(args.profile))
    except (ValueError, OSError) as error:
        parser.exit(1, f"quantum run failed - {error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    quantum = report["quantum"]
    print(f"exact util - {report['exact']['utility']:.6f}")
    print(f"sample util - {quantum['raw_best_utility']}")
    print(f"feasible shots - {quantum['feasible_shot_rate']:.3f}")
    print(f"evals - {quantum['objective_evaluations']}")
    print(f"report - {args.output}")
    return 1 if quantum["best_sample"] is None else 0


if __name__ == "__main__":
    raise SystemExit(main())
