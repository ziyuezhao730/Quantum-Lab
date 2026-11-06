"""Independent checks for Risi's exact study planner (FR05).

Written from docs/01_requirements.md (sections 6 and 8), not from the
implementation's output. Every expected number comes from
data/demo/oracle.json, which was hand-calculated from the specification.

Run from the repository root:
    python -m pytest tests/test_optimizer.py -q
"""

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.optimizer.classical import solve_exact  # noqa: E402

ORACLE_PATH = ROOT / "data" / "demo" / "oracle.json"
TOPICS = ("T1", "T2", "T3")


def load_oracle():
    with ORACLE_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


ORACLE = load_oracle()
WEIGHTS = ORACLE["test_weights"]


def reference_utility(allocations, weights, proficiency):
    """V = sum_i (a_i * x_i1 + 0.5 * a_i * x_i2), rebuilt from the spec."""
    total = 0.0
    for topic_id, minutes in allocations.items():
        a_i = weights[topic_id] * (1.0 - proficiency[topic_id])
        if minutes >= 30:
            total += a_i
        if minutes == 60:
            total += 0.5 * a_i
    return total


@pytest.mark.parametrize("case", ORACLE["cases"], ids=[c["case_id"] for c in ORACLE["cases"]])
def test_known_optimal_plan(case):
    result = solve_exact(WEIGHTS, case["proficiency"], case["budget_minutes"])

    assert result["allocations"] == case["expected_allocation"]
    assert math.isclose(
        result["utility"],
        case["expected_utility"],
        abs_tol=case["utility_tolerance"],
    )
    assert result["feasible"] is True
    assert result["actual_solver"] == "exact"
    assert result["execution_mode"] == "live"


@pytest.mark.parametrize("case", ORACLE["cases"], ids=[c["case_id"] for c in ORACLE["cases"]])
def test_reported_utility_matches_independent_recalculation(case):
    result = solve_exact(WEIGHTS, case["proficiency"], case["budget_minutes"])

    rebuilt = reference_utility(result["allocations"], WEIGHTS, case["proficiency"])

    assert math.isclose(result["utility"], rebuilt, abs_tol=1e-9)


@pytest.mark.parametrize("case", ORACLE["budget_cases"], ids=[str(c["budget_minutes"]) for c in ORACLE["budget_cases"]])
def test_budget_limits(case):
    budget = case["budget_minutes"]
    result = solve_exact(WEIGHTS, case["proficiency"], budget)
    allocations = result["allocations"]

    assert set(allocations) == set(TOPICS)
    for minutes in allocations.values():
        assert minutes in (0, 30, 60)
        assert not isinstance(minutes, bool)

    assert result["used_minutes"] == sum(allocations.values())
    assert result["unused_minutes"] == budget - result["used_minutes"]
    assert result["used_minutes"] <= budget
    assert result["used_minutes"] <= 30 * (budget // 30)

    if "expected_allocation" in case:
        assert allocations == case["expected_allocation"]
    if "max_used_minutes" in case:
        assert result["used_minutes"] <= case["max_used_minutes"]


def test_second_block_never_comes_without_the_first():
    """A later 30-minute block may only appear when the first block is present."""
    for budget in (0, 30, 60, 90, 120, 180):
        result = solve_exact(WEIGHTS, {"T1": 0.3, "T2": 0.3, "T3": 0.3}, budget)
        for minutes in result["allocations"].values():
            assert minutes in (0, 30, 60)


@pytest.mark.parametrize("budget", [-30, 181, 90.5, "90", None, True])
def test_rejects_invalid_budget(budget):
    with pytest.raises((ValueError, TypeError)):
        solve_exact(WEIGHTS, {"T1": 0.5, "T2": 0.5, "T3": 0.5}, budget)


@pytest.mark.parametrize(
    "weights, proficiency",
    [
        ({"T1": 1.0, "T2": 1.0}, {"T1": 0.5, "T2": 0.5, "T3": 0.5}),
        (WEIGHTS, {"T1": 0.5, "T2": 0.5}),
        ({"T1": 1.0, "T2": 1.0, "T3": 1.0, "T4": 1.0}, {"T1": 0.5, "T2": 0.5, "T3": 0.5}),
    ],
)
def test_rejects_missing_or_extra_topic_keys(weights, proficiency):
    with pytest.raises(ValueError):
        solve_exact(weights, proficiency, 90)


def test_plan_result_shape():
    result = solve_exact(WEIGHTS, {"T1": 0.2, "T2": 0.4, "T3": 0.6}, 60)

    for key in (
        "allocations",
        "used_minutes",
        "unused_minutes",
        "utility",
        "feasible",
        "actual_solver",
        "execution_mode",
        "elapsed_ms",
        "warnings",
        "quantum_metrics",
    ):
        assert key in result

    assert result["warnings"] == []
    assert result["quantum_metrics"] is None
