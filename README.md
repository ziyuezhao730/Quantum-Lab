# examace

study scheduling with a Qiskit QAOA comparison, built for Qiskit Fall Fest 2026.

a short calculus diagnostic sets topic priorities. the planner selects compatible
study sessions around availability, preparation requirements & exam deadlines.
practice questions stay linked to the reviewed fictional course material.

## run
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```
open http://127.0.0.1:8501

## demo
six-question dialog, budget & availability, build a schedule, Practice, Quantum lab.
start with 10 hours & three planning days to see the interacting example.
all computation runs locally after installation. profiles contain no identity fields.

## comparison
```bash
python3 scripts/benchmark_scheduler.py
python3 -m src.optimizer.quantum_demo --profile runtime/student_profile.json
```
27 recorded runs compare exact, greedy, QAOA & uniform sampling.
results - evidence/risi/scheduler_results.md
model - docs/scheduler.md
presentation - docs/delivery/final_demo.md
beginner guide with source - evidence/risi/scheduler_guide.pdf
current handoff - docs/delivery/results.md
setup - HOW-TO-RUN.md

## scope
one fictional calculus course, six diagnostic & six practice questions.
QAOA uses an ideal local simulator. the benchmark measures this planning objective.

## team
Ziyue Zhao, Risi Chen, Charlie Chen, Hank Ruan.
team branch history & contributions are preserved in the integration.
ai assistance supplied implementation, integration, local validation & explanations.
