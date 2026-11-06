examace - local setup

python 3.11 was verified on macos. other platforms must install compatible wheels.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py --server.address 127.0.0.1
```

open http://127.0.0.1:8501 in your browser.
windows activation - .venv\Scripts\Activate.ps1

checks
```bash
python3 -m pytest tests/ evidence/risi/check_quantum_model.py evidence/risi/check_qaoa.py evidence/risi/check_r4.py -q
python3 scripts/smoke.py
```

dashboard workflow
1. answer the one-question-at-a-time diagnostic dialog, shown once per browser session.
2. set hours & extra minutes in the sidebar, up to 24 hours total.
3. build the plan, use Study plan / Practice / Quantum lab tabs.
4. changing the budget or retaking the diagnostic clears old plans & comparisons.

fictional case-a answers in question order - A, B, A, B, C, A.
10-hour budget gives 450 study minutes, 135 break minutes & 15 minutes spare.
case-a allocations - T1=0, T2=285, T3=165 minutes.
all data stays in session memory. a page reload starts a new browser session.


quantum handoff
1. use the app with fictional demo answers, generate a plan & download profile json.
2. save it as runtime/student_profile.json. keep real student exports out of git.
3. in an activated terminal, run
```bash
python3 -m src.optimizer.quantum_demo --profile runtime/student_profile.json
```

saved comparison replay - no new quantum run
```bash
python3 -m evidence.risi.replay_comparison
```

a pipeline-only fictional export is also available
```bash
python3 -m evidence.risi.export_fictional_profile
```

all computations run offline after dependencies are installed.
the app uses exact planning & offers a bounded local comparison in Quantum lab.
schema-2 exports also work with the separate quantum command.
the original schema-1 experiment remains supported independently.
no api keys, accounts, network services or quantum hardware are required.
source & dependency changes require rerunning these checks before release.
