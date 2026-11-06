interacting scheduler - #45

input - scored fictional profile, total time budget, available windows & topic exam days.
choices - up to 18 review/practice sessions across three days, 15/30/45-minute focus lengths.
constraints - availability, deadline, overlap including 15-minute breaks, total budget,
& one earlier selected review before a practice session that requires preparation.
objective - weighted score gap, exam urgency, practice value & reduced repeat value.

one qubit per candidate session, bit 1 selects that session.
energy = -session utility + P*constraint violations.
P is greater than the sum of all positive session values.
invalid budget excess is counted in 15-minute units with upward rounding.

exact reference enumerates the small model. greedy adds the next compatible improvement.
QAOA uses one cost/mixer layer & a budget-aware product starting state.
Qiskit ry prepares it, Statevector carries amplitudes, rx applies the mixer,
Statevector.sample_counts supplies actual measured candidate strings.
the diagonal cost phase is evaluated directly with numpy, scaled by P.
this is ideal statevector simulation; no circuit was submitted to hardware.

versions - schema 1 original experiment, schema 2 long allocation, schema 3 interacting schedule.
quantum_demo --profile dispatches without changing older evidence.
recorded benchmark source - 3dfb985, clean tree at execution.
full settings, profiles, answers, results & one raw run are in evidence/risi/.

new local validation - independent small-instance enumeration, budget edges,
diagnostic flow, interacting plan, QAOA tab & stale-state clearing after deadline edits.
no new test files committed for this feature, per user request.
