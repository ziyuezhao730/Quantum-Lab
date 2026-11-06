examace ui - integrated workflow

app.py calls validated course loading, key-based diagnostic scoring, snapshot export,
exact planning & approved-practice retrieval. fixed test scores are removed.

src/ui/inputs.py retains charlie's unanswered radio controls & change callback.
integer budget - 0..180, step 1. callback drops the saved plan immediately.
one generate button runs the pipeline. snapshot download appears only after submission.

results show Initial topic score from two questions, used/unused minutes,
exact/live labels, topic allocation & source-linked practice with answer reveals.
practice includes difficulty & matching reason. null answers & shortages are labelled.
profile download is the shared ProfileSnapshot schema, no identity fields.

verification - tests/test_ui.py, tests/test_retrieval.py & tests/test_intelligence.py
142 tests pass in the full relevant suite, no skips. smoke passes.
real browser - case-a submitted, 0/60/30 plan displayed, profile downloaded,
budget edit cleared old output/download, plan regenerated.

charlie's earlier screenshots describe the previous test-mode branch.
new browser screenshot - evidence/risi/app_results.jpg
ai assistance - codex integrated the existing ui & supplied retrieval/tests.
no independent human review or personal rehearsal claimed.
