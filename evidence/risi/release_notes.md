r4 & r5 handoff

tested code commit - 545b1484eaed5c2ad171a854e03f88e4829f820f
comparison source commit - 2a74c42ab4f064e7fdd72584be09d7c86669c45c
comparison recorded clean tree - True
branch - risi/r4-r5-evidence, stacked on r3 & r2

commands actually run
```bash
source .venv/bin/activate
python3 -m pytest tests/ evidence/risi/check_quantum_model.py evidence/risi/check_qaoa.py evidence/risi/check_r4.py -q
python3 -m evidence.risi.replay_comparison
python3 scripts/smoke.py
```

results
- 127 passed, 6 skipped
- skipped - retrieval cases, production ranking & reviewed top-id oracle missing
- 1 existing warning - duplicate allocation-key validator in contracts.py
- replay passed, original snapshot retained, cached_replay label shown
- smoke exit 2 - scoring, snapshot & exact passed, practice retrieval incomplete
- git diff --check passed
- guide - 57 pages rendered & visually inspected, code included

r4 result
- profile - fictional case-a, exported through production scoring & snapshot functions
- not a streamlit download, no real student data
- scores - t1=1, t2=0, t3=.5
- weights - t1=5/6, t2=2/3, t3=5/6
- budget - 90 mins
- exact - 0/60/30, util 1.416667
- sampled - 0/30/0, util .666667
- gap - .75
- feasible shots - 86/1024
- qaoa - 9 qubits, p=1, seed 7, 30 evaluations, one start
- optimizer hit the cap, did not converge
- timings in r4_comparison.json, complete quantum attempt included
- no speedup, quantum advantage or learning gain claim

r5 materials ready
- quantum_guide.pdf - beginner explanation, worked examples, actual code & presentation route
- demo_script.md - replay walkthrough & expected numbers
- code_notes.md - text reference for functions
- fictional_profile.json & r4_comparison.json - retained evidence
- check_r4.py - rejects changed result fields & profile
- tests/test_intelligence.py - scoring, invalid inputs, course validation, snapshot roundtrip

remaining release gates
- src/intelligence/rank.py is empty here, six at05 checks cannot run
- data/demo/retrieval_cases.json is empty here, reviewed retrieval oracle required
- app.py & src/ui implementation are empty here, ui prs are not integrated
- no integrated website to launch/test on this branch
- review & merge required, no independent review claimed
- run final checks again on merged release candidate
- risi still needs to read the guide & rehearse, assistant cannot perform personal understanding
- no real presentation recording created or event deadline verified here
- do not label the integrated product v2.1 until its remaining core gates pass

ai assistance
codex implemented binary/ising helpers, bounded qaoa adaptation, report export,
replay audit, verification tests & teaching materials, ran commands & inspected
pdf renders. original project scaffold & interfaces came from the team.
no statement that risi manually recomputed every value or independently reviewed
the assistant's own code is implied.

observed defects & fixes
- topic weight limit allowed 10, corrected to 1
- invalid-order tutorial example was 1.6, hand calculation corrected to 1.9
- renaming a test's global weights created a local-variable collision, fixed
- r1 hand-calculation header listed unequal weights while using unit weights, corrected
- r3 evidence was generated before its source commit, r4 regenerated on clean committed source

website test after integration
```bash
python3 -m streamlit run app.py
```
1. six choices start unanswered, budget accepts integer 0..180.
2. incomplete answers show a readable error, no plan.
3. case-a answers + 90 minutes give scores 1/0/.5, actual weights, plan 0/60/30.
4. downloaded snapshot matches scores, weights & budget.
5. changing any answer or budget immediately clears plan, practice & download.
6. zero budget gives zero study time & readable empty state.
7. practice includes approved practice items only, from allocated topics, no diagnostic items.
8. case-b at the same budget changes the relevant allocation/practice topics.
9. saved quantum replay keeps case-a inputs even after app answers change.
status - pending, no website pass claimed.


clean-environment verification
- local clone of committed source 545b148 into /private/tmp/examace-release-check/clone
- separate python 3.11 environment, installed evidence/risi/requirements-qaoa.txt
- same machine, not a second-machine claim
- 127 passed, 6 retrieval checks skipped, 1 existing validator warning
- saved replay passed
- required quantum command ran successfully in clean clone
- same sampled utility, feasible-shot count & gap reproduced with seed 7
- original r4 evidence retained, this extra run is a reproducibility check
- integrated app setup remains unverified because app & ranking are empty here
