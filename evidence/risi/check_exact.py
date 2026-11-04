from math import isclose
from src.optimizer.classical import solve_exact

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

# equal priorities: prefer the earlier topic.
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

print("additional checks passed")