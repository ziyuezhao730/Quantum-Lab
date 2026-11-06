risi demo - saved comparison

before presenting
```bash
source .venv/bin/activate
python3 -m evidence.risi.replay_comparison
```
show cached_replay, original profile, exact/sample allocations, gap & feasible rate.
this reads saved evidence, no new quantum attempt.

say in about 60 seconds
examace allocates study time from a short diagnostic & a time budget.
i implemented an exact planner over 27 possible allocations.
we express the same objective & constraints as a nine-bit energy model.
six bits select study blocks, three encode unused blocks.
penalties catch overspending, incorrect slack & selecting second blocks without first blocks.
i adapted the library's one-layer qaoa circuit & simulated it locally.
both solvers used the same exported fictional profile.
exact utility was 1.416667, best feasible sampled utility was .666667.
86 of 1024 shots were feasible. optimization hit its 30-evaluation cap.
this checks our model & sampled feasibility, it does not establish quantum advantage or learning gains.

if asked why the result is worse
one shallow circuit, one start & a strict evaluation budget do not guarantee the optimum.
we report the sampled result without substituting the exact answer.

if asked why nine qubits when exact has 27 plans
the six block bits allow invalid combinations too, three slack bits encode unused blocks.
we penalize invalid binary combinations & independently filter sampled feasibility.

if asked what you personally checked
state what you actually read, ran & understood. explain ai assistance explicitly.

personal rehearsal - pending until risi does it
recording - pending, no recording claimed
