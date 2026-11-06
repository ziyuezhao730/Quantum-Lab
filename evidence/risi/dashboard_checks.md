dashboard verification - #41

command
python3 -m pytest tests/ evidence/risi/check_quantum_model.py evidence/risi/check_qaoa.py evidence/risi/check_r4.py -q
result - 169 passed, no skips.

new checks
- 0..1440 minute budgets, 15-minute slots, contiguous timelines & break accounting
- exact harmonic allocation agrees with independent enumeration on small cases
- count-register minimum energy agrees with exact utility
- real 10-hour quantum attempt gives a feasible sampled plan
- 6-step dialog, retake & one-time session behavior
- plan/profile/quantum stale state cleared after settings changes
- schema 1 stays compatible, schema 2 export/cli roundtrip works

real browser
- fictional case-a diagnostic completed through all six dialog steps
- 10-hour plan displayed 7h30 study, 2h15 breaks, 15m spare
- practice tab contains only allocated-topic reviewed questions
- schema-2 session profile downloaded successfully
- quantum tab returned exact & sampled priority value about 3.623,
  10 qubits, 30 evaluations, about 63.3% feasible samples
- one local simulation only, no hardware or advantage claim

remaining - independent human review, personal preparation, team recording & event submission.
