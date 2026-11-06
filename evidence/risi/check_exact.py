from math import isclose
from src.optimizer.classical import solve_exact, is_feasible
from src.contracts import PlanRequest, PlanResult
from src.optimizer.classical import solve_plan

weights = {"T1": 1.0, "T2": 1.0, "T3": 1.0}
scores = {"T1": 0.8, "T2": 0.2, "T3": 0.4}
budget = 90
result = solve_exact(weights, scores, 90)
print(result)

assert result["allocations"] == {"T1": 0, "T2": 60, "T3": 30}
# accounts for floating point issues, 1e-8 value subject to change
assert isclose(result["utility"], 1.8, abs_tol=1e-8)
assert result["used_minutes"] == 90
assert result["unused_minutes"] == 0

print("example passes")


# partial block remains unused.
result = solve_exact(weights, scores, 45)
assert result["allocations"] == {"T1": 0, "T2": 30, "T3": 0}
assert result["unused_minutes"] == 15

# budget below 30 cannot buy a block.
result = solve_exact(weights, scores, 15)
assert result["used_minutes"] == 0
assert result["unused_minutes"] == 15

# no remaining benefit, prefers the empty plan.
all_correct = {"T1": 1.0, "T2": 1.0, "T3": 1.0}
result = solve_exact(weights, all_correct, 180)
assert result["used_minutes"] == 0

# equal priorities, prefer the earlier topic.
all_wrong = {"T1": 0.0, "T2": 0.0, "T3": 0.0}
result = solve_exact(weights, all_wrong, 30)
assert result["allocations"] == {"T1": 30, "T2": 0, "T3": 0}

# changing the student changes plan
student_a = {"T1": 1.0, "T2": 0.0, "T3": 0.5}
student_b = {"T1": 0.0, "T2": 1.0, "T3": 0.5}

assert solve_exact(weights, student_a, 90)["allocations"] == {
    "T1": 0, "T2": 60, "T3": 30
}
assert solve_exact(weights, student_b, 90)["allocations"] == {
    "T1": 60, "T2": 0, "T3": 30
}

# boundary cases
for budget in (0, 15, 45, 180):
    result = solve_exact(weights, scores, budget)
    assert result["feasible"]
    assert is_feasible(result["allocations"], budget)
    assert result["used_minutes"] == sum(result["allocations"].values())
    assert result["unused_minutes"] == budget - result["used_minutes"]

    if budget < 30:
        assert result["used_minutes"] == 0
    if budget == 45:
        assert result["used_minutes"] == 30

# feasibility checks
assert not is_feasible({"T1": 60, "T2": 60, "T3": 0}, 90)
assert not is_feasible({"T1": 45, "T2": 0, "T3": 0}, 90)
assert not is_feasible({"T1": 90, "T2": 0, "T3": 0}, 180)
assert not is_feasible({"T1": 0, "T2": 0}, 90)

# label checks
result = solve_exact(weights, scores, 90)

assert result["actual_solver"] == "exact"
assert result["execution_mode"] == "live"
assert result["elapsed_ms"] >= 0
assert result["warnings"] == []
assert result["quantum_metrics"] is None

# invalid input

bad_inputs = [
    (weights, scores, -1),
    (weights, scores, 181),
    (weights, scores, 30.5),
    (weights, scores, True),
    ({"T1": 1.1, "T2": 1.0, "T3": 1.0}, scores, 90),
    (weights, {"T1": float("nan"), "T2": 0.2, "T3": 0.4}, 90),
]

for test_weights, test_scores, test_budget in bad_inputs:
    try:
        solve_exact(test_weights, test_scores, test_budget)
    except ValueError:
        pass
    else:
        raise AssertionError("error: accepts invalid input")

print("additional checks passed")

rq = PlanRequest(budget_minutes=90, proficiency=scores, requested_solver="exact")

plan = solve_plan(weights, rq)

assert isinstance(plan, PlanResult)
assert plan.allocations == {"T1": 0, "T2": 60, "T3": 30}
assert isclose(plan.utility, 1.8, abs_tol=1e-8)
assert plan.feasible
assert plan.used_minutes == 90
assert plan.unused_minutes == 0
assert plan.actual_solver == "exact"
assert plan.execution_mode == "live"

print(plan.model_dump())

rq = PlanRequest(budget_minutes=90, proficiency=scores, requested_solver="qaoa")
try:
    solve_plan(weights, rq)
except ValueError:
    pass
else:
    raise AssertionError("exact planner solve quantum")

print("planner interface checks passed")