"""audit & show saved evidence, no new quantum run"""
import argparse
import json
from math import isclose, isfinite
from pathlib import Path

from src.intelligence.validate import validate_snapshot
from src.optimizer.classical import solve_plan
from src.optimizer.quantum_demo import select_sample


def audit_report(report):
    """reject changed inputs, mismatched results or incomplete evidence"""
    snapshot = validate_snapshot(report["profile"])
    quantum = report["quantum"]
    exact = solve_plan(snapshot.topic_weights, snapshot.request.model_copy(update={"requested_solver": "exact"}))
    def check(condition, message):
        if not condition:
            raise ValueError(message)
    check(report["execution_mode"] == quantum["execution_mode"] == "live", "original evidence must be a live run")
    check(report["working_tree_dirty"] is False, "evidence source was uncommitted")
    check(len(report["code_commit"]) == 40, "missing source commit")
    check(quantum["qubits"] == 9 and quantum["p"] == 1, "wrong circuit size")
    check(quantum["seed"] == 7 and quantum["shots"] == 1024, "wrong sampling settings")
    check(0 < quantum["objective_evaluations"] == len(quantum["trace"]) <= 30, "wrong eval budget")
    check(sum(quantum["counts"].values()) == 1024, "wrong shot total")
    check(all(type(n) is int and n > 0 for n in quantum["counts"].values()), "invalid counts")
    check(exact.allocations == report["exact"]["allocations"], "exact allocation changed")
    check(isclose(exact.utility, report["exact"]["utility"], abs_tol=1e-8), "exact utility changed")
    best, bits, rate = select_sample(quantum["counts"], snapshot.topic_weights, snapshot.request)
    check(best == quantum["best_sample"] and bits == quantum["best_bits"], "saved sample changed")
    check(isclose(rate, quantum["feasible_shot_rate"], abs_tol=1e-12), "feasible rate changed")
    util = None if best is None else best["utility"]
    check(util == quantum["raw_best_utility"], "sample utility changed")
    gap = None if util is None else abs(exact.utility-util)
    check(gap == report["absolute_utility_gap"], "utility gap changed")
    for result in (quantum, report["exact"]):
        check(isfinite(result["elapsed_ms"]) and result["elapsed_ms"] >= 0, "invalid timing")
    return snapshot


def main():
    parser=argparse.ArgumentParser(description="replay saved fictional-profile comparison")
    parser.add_argument("--report", type=Path, default=Path(__file__).with_name("r4_comparison.json"))
    args=parser.parse_args()
    report=json.loads(args.report.read_text())
    snapshot=audit_report(report)
    print("cached_replay - saved local simulation, no new run")
    print(f"original run - {report['created_utc']}")
    print(f"profile - {snapshot.request.model_dump()}")
    print(f"exact - {report['exact']['allocations']}, util {report['exact']['utility']:.6f}")
    print(f"sample - {report['quantum']['best_sample']}")
    print(f"gap - {report['absolute_utility_gap']:.6f}")
    print(f"feasible rate - {report['quantum']['feasible_shot_rate']:.6f}")


if __name__ == "__main__":
    main()
