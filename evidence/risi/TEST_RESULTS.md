# Model validation checks

Run on November 3, 2026 using Pydantic 2.11.7 and pytest 9.1.1.

Command: `python3 -m pytest tests/test_models.py -q`

- Original supplied models: **50 passed, 1 failed**.
- After the allocation-key fix: **51 passed**.

The suite has 15 test functions; parameterized inputs produce 51 cases.

## Checklist

- [x] Budget endpoints 0 and 180 accepted; negative, above-180, fractional, and boolean budgets rejected.
- [x] Proficiency requires exactly T1, T2, T3; values include valid endpoints and reject negative, above-one, NaN, and infinity inputs.
- [x] Requested and actual solvers accept exact and qaoa and reject representative invalid inputs.
- [x] Allocations require exactly T1, T2, T3; 0, 30, 60 accepted and other representative values rejected.
- [x] Execution mode accepts live and cached_replay and rejects representative invalid inputs.
- [x] Negative and non-finite utility and elapsed_ms rejected.
- [x] QuantumMetrics enforces positive qubits/p/shots, nonnegative seed, and finite feasible_shot_rate within [0, 1].
- [x] raw_best_utility and quantum_metrics default to None and accept explicit None and valid populated values. Invalid raw utility and nested metrics inputs rejected.
- [x] Request, metrics, and result examples survive JSON serialization and reload with equal values, including nested metrics, warnings, and null defaults.
- [x] Actual results and fix recorded here.

## Defect and fix

The original `PlanResult.allocations` annotation validates dictionary values but does not validate topic names. The exact-topic test failed because an empty allocation dictionary was accepted. The same annotation also permits missing, extra, and substituted topic keys.

Added `PlanResult.check_allocation_keys`, a field validator requiring exactly T1, T2, and T3, matching the existing request-side proficiency validation. The final run checks empty, missing, extra, and substituted allocation keys and passes.

Only this validator was added to the supplied models. Allocation values retain Pydantic Literal semantics, which accept numerically equal inputs such as 30.0; strict allocation input types were not part of this checklist.
