current handoff - interacting scheduler

source for recorded benchmark - 3dfb985, clean tree during runs.
27 runs, 12/15/18 choices, seeds 7/11/23, p=1, 30 evaluations, 1024 shots.
all found feasible sampled schedules. mean sampled/exact score 85.1%.
mean feasible-shot rate 8.2%, earlier starting state 2.8%.
full cases, settings & results - evidence/risi/scheduler_benchmark.json
full sample counts & trace - evidence/risi/scheduler_example.json

local validation - 2026-11-06, python 3.11 on macos
- 160 existing automated checks passed
- independent small scheduling enumeration & budget edge checks passed
- diagnostic dialog, ten-hour schedule, ranked practice & live Qiskit comparison passed
- editing a deadline cleared the old plan & comparison
- git diff --check passed
- new scheduler checker files stayed outside the repository

commands
```bash
python3 -m pytest -p no:cacheprovider tests/ evidence/risi/check_quantum_model.py evidence/risi/check_qaoa.py evidence/risi/check_r4.py -q
python3 scripts/smoke.py
python3 -m streamlit run app.py
python3 -m src.optimizer.quantum_demo --profile runtime/student_profile.json
```

current model - docs/scheduler.md
current demo - docs/delivery/final_demo.md
current beginner guide with source - evidence/risi/scheduler_guide.pdf
prior reports remain historical evidence for the original allocation experiments.

remaining human work - independent review, personal rehearsal, team recording,
confirm event submission details & submit. no completion claim for these steps.

ai assistance - codex implemented the expanded scheduler & Qiskit experiment,
integrated team branches, ran local validation, generated comparison evidence,
prepared the guide & demo material. risi directed scope & product copy.
