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
