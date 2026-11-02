# ExamAce Team Work Packages

Individual requirements and handoff checks

Risi owns the decision engine, Alex diagnostic scoring and content intelligence, Charlie the student workflow, and Hank verification and delivery. Read this page and your own package. Use Document 01 for shared contracts.

## 1 Equal capacity and shared expectations

Plan for ninety minutes per person each night: sixty minutes of focused implementation, fifteen minutes of checking and review, and a fifteen-minute stand-up. Across five days this is 450 minutes per person, or thirty team hours. Setup, debugging, small explanations, and documentation are included. Optional lectures add calendar time and do not create extra project obligations.

Treat ninety minutes as a hard limit, not a promise that every feature takes the same effort. Within the sixty-minute work block, aim for forty-five minutes on one small core outcome and preserve fifteen minutes for setup, debugging, or explanation. The check and stand-up blocks remain separate. If blocked, report after ten minutes; adjust the next slice instead of adding hours.

| Workstream | Implements | Independent checks | Reviews |
| --- | --- | --- | --- |
| Decision engine | Risi | Hank | Alex |
| Content intelligence | Alex | Risi | Charlie |
| Student workflow | Charlie | Alex | Hank |
| Fixtures and delivery | Hank | Charlie | Risi |

The checker writes a small test or a concrete manual procedure on the implementation branch and runs it; only the checker edits that assigned check file. The third person reviews both changes against the requirement. These roles adapt SE101 Lab 5 to this project. Document 03 gives the commands for the shared PR.

## 2 Daily handoff format

Each PR records its requirement, files, input/output example, checker result, reviewer, and limitations. Include specific AI assistance and what you checked or changed. Follow any additional event disclosure rule.

Before handing off a change, explain one input, one output, one failure case, and one design choice. Add two or three sentences to your own component note while the code is fresh. This takes place during implementation and review, not in a later study session.

AI may draft code, data, tests, and prose. Run and understand the result. Keep changes small and inside agreed files.

Optional items OP01 to OP08 in Document 01 are unassigned. Anyone may claim one voluntarily after core work is checked. No daily package includes an optional quota, and nobody inherits unclaimed work. A complete core release needs none of those extensions.

## 3 Start order

Hank creates the common skeleton and ignored-file rules in the first fifteen minutes of Day 1. During that time, Risi works through AT01, Alex checks the contract example, and Charlie sketches the single-screen flow. Everyone then pulls the baseline in their existing clone, or clones once, and branches from main. A component may use a clearly marked stub until its dependency lands.

## 4 Risi work package

### Objective and owned outputs

Deliver the exact study planner and one separate exported-profile quantum experiment for FR05, FR07, and FR08. Reusing a documented circuit template is the intended core approach.

Own src/optimizer/model.py, classical.py, and quantum_demo.py; docs/model.md; and evidence/risi/. Own tests/test_intelligence.py as Alex's independent checker. Hank owns tests/test_optimizer.py. Do not edit the UI, fixtures, or shared contracts directly.

### Required steps

1. Implement block utilities, feasibility checks, and the twenty-seven-allocation exact reference. Use AT01's hand calculation to verify the result and the tie rule.
2. Implement Document 01 section 7's supplied coefficient formulas for three topics and three slack bits. Accept validated profile scores, weights, and budget. Check known energies and bit ordering; no general-purpose converter is required.
3. Adapt one documented Qiskit example using its library QAOA ansatz and local simulator. Reuse the circuit template and mixer. Do not build a custom gate sequence or general solver framework.
4. Read runtime/student_profile.json and compare both solvers on identical problem data. Produce one report for that exported profile, including feasibility, utility gap, timings, and limitations. App wiring is optional OP02; extended benchmarking is OP04.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min oracle and contract; 30 min exact-solver first pass; 15 min buffer. | Inspectable allocator, or explicit stub and blocker. |
| 2 | 25 min exact checks; 20 min supplied coefficient formula; 15 min buffer. | Exact result ready for V1. |
| 3 | 45 min adapt the library ansatz to a sample exported profile; 15 min buffer. | One bounded experiment attempt. |
| 4 | 25 min run the submitted profile; 20 min report and decode checks; 15 min buffer. | Student-profile quantum evidence. |
| 5 | 25 min core fixes; 20 min rehearse and finalize note; 15 min buffer. | Verified contribution, no optional quota. |

Keep the additional fifteen-minute check block and fifteen-minute stand-up. If adaptation is blocked, share the failing example promptly; do not add custom features or promise overtime.

### Acceptance and explanation

Hank checks AT01, AT02, and the known examples in AT07. Alex reviews that both solvers receive the same snapshot data and that result labels are accurate. Explain the objective, constraints, library template, sampled feasibility, and why this experiment establishes no quantum advantage. Exhaustive energy scans and custom gates are optional.

In docs/model.md, retain the hand calculation, adapted-example reference, specific changes, an observed defect and fix if encountered, and the single run report. These support a precise optimization resume claim without implying an original quantum framework.

## 5 Alex work package

### Objective and owned outputs

Deliver validated diagnostic scoring, a profile snapshot, and practice retrieval for FR02, FR03, and FR06. JSON loading is the core input; PDF extraction moves to optional OP01 to make room for personalization.

Own src/contracts.py; src/intelligence/assess.py, validate.py, pipeline.py, and rank.py; docs/pipeline.md; and evidence/alex/. Own tests/check_ui.md as Charlie's independent checker. Risi owns tests/test_intelligence.py. Charlie alone edits application screens.

### Required steps

1. Validate reviewed JSON, the two diagnostic/two practice records per topic, choices, answer keys, sources, and counts. Share one passing course and snapshot example on Day 1.
2. Score six choice IDs into three fractions correct. Reject incomplete and invalid answers. Build and validate the snapshot from this result, current budget, and computed weights; no identity or history model.
3. Retrieve approved practice items only using topic filtering, TF-IDF, score-based difficulty matching, and the fixed tie rule. Diagnostic questions must never appear in practice.
4. Compute importance from reviewed counts. Check scoring, export round-trip, and six frozen top-result cases. Preserve actual outcomes. AI-based assessment, PDF parsing, and embeddings remain optional.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min course/snapshot examples; 30 min validation and loader; 15 min buffer. | Valid shared data boundary. |
| 2 | 30 min diagnostic scoring; 15 min importance and snapshot; 15 min buffer. | Validated profile ready for UI and model. |
| 3 | 45 min practice filtering and ranking; 15 min buffer. | Score-to-practice path connected. |
| 4 | 25 min query and error checks; 20 min fixes and evidence; 15 min buffer. | Core pipeline checked. |
| 5 | 25 min core fixes; 20 min trace rehearsal and note; 15 min buffer. | Verified contribution, no optional quota. |

Use the separate check block for Charlie's UI procedure and Risi's result review. If integration is blocked, share the smallest failing answer set or snapshot. Keep the six-item key-based scoring rule; do not add AI marking or a confidence-blending model.

### Acceptance and explanation

Risi checks scoring/export in AT06, validation in AT04, and ranking in AT05 during the allocated check blocks. Charlie reviews the trace from an answer through its topic score to practice. Explain key-based scoring, validation, ranking, and the limits of two questions per topic.

In docs/pipeline.md, retain one answer-to-profile example, the scoring and ranking rules, actual query results, and one observed defect and fix if encountered. Describe diagnostic-based personalization and validated retrieval; claim AI assessment only if separately implemented and checked.

## 6 Charlie work package

### Objective and owned outputs

Deliver the student-facing workflow for FR04 and the presentation parts of FR06 and FR09. A student should understand the plan, find the associated questions, and recognize whether a displayed experiment is a simulation or a saved replay.

Own app.py, src/ui/inputs.py, src/ui/results.py, docs/ui.md, and evidence/charlie/. Own tests/test_fixtures.py as Hank's independent checker. Alex writes tests/check_ui.md. Do not implement ranking rules or optimizer math inside the UI.

### Required steps

1. Build one Streamlit page with six standard choice controls and a budget field on one screen using ordinary widgets and one planning button. Each choice starts unanswered. This replaces the three confidence sliders; do not build both input paths.
2. Call Alex's scorer and snapshot builder, then Risi's exact planner and Alex's retriever. Show initial topic scores, allocations, used/unused time, and practice with source labels and available answer reveals.
3. Use change callbacks and one planning button; avoid st.form so input edits immediately clear stale output. On any changed answer or budget, clear results and the snapshot download until resubmission; use standard change callbacks/session state. Add one download button for Alex's snapshot JSON. No quantum controls or background jobs.
4. Label the plan exact classical optimization and the scores initial results from two questions per topic. A saved quantum report represents only its recorded snapshot; it does not automatically follow later app inputs.
5. Use standard readable validation and empty-state messages. No custom graphics, independent UI scoring, or additional exports are required.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min sketch; 30 min six-choice form and budget; 15 min buffer. | V0 accepts a profile. |
| 2 | 45 min wire scoring, exact plan, and practice display; 15 min buffer. | First V1 flow. |
| 3 | 25 min invalidation; 20 min snapshot download and source labels; 15 min buffer. | V1 checked end to end. |
| 4 | 25 min end-to-end corrections; 20 min labels and empty states; 15 min buffer. | Core screens checked. |
| 5 | 20 min core fixes; 25 min rehearsal and note; 15 min buffer. | Verified release contribution. |

Use the checking block to check fixture records and review Alex's pipeline changes. Trace the input/output examples and reproduce any unclear behavior with the owner.

### Acceptance and explanation

Alex checks AT03, AT08, the zero-time screen, and missing-answer behavior. Hank reviews the flow from a clean launch. Charlie can explain where session state is used, when cached output becomes stale, how one button triggers scoring, planning, retrieval, and snapshot construction, and how the user sees an input or planning failure.

In docs/ui.md, record the screen flow, input rules, invalidation rule, and a screenshot tied to the release. A completed contribution can be described as building an interactive study-planning and practice workflow, including state handling and clear experiment results.

## 7 Hank work package

### Objective and owned outputs

Deliver reproducible data, independent verification, and a dependable demo for FR01 and FR10. The release must be runnable by someone other than its implementers and backed by traceable checks.

Own data/demo/, scripts/smoke.py, requirements.in, requirements.txt, .gitignore, README.md, HOW-TO-RUN.md, docs/decisions.md, docs/delivery/, and evidence/hank/. Own tests/test_optimizer.py as Risi's independent checker. Charlie owns tests/test_fixtures.py. Each member owns their own stand-up note.

### Required steps

1. Create the shared repository baseline and placeholders from Document 03. Exclude credentials, runtime uploads, caches, and environments. Record the agreed Python version and lock the working dependencies from a clean environment.
2. Keep twelve original questions, four per topic: two diagnostic multiple-choice items with checked keys and two distinct practice items. Supply reviewed counts/excerpts from three short authored assessments. Use simple authored source labels/pages; no PDF typesetting. AI may draft records; manually verify mathematics and keys.
3. Prepare Student A/B fictional response sets, the model oracle, six retrieval cases with acceptable top-ranked practice IDs, and malformed records. Keep test-only unit weights separate from actual demo weights.
4. Write optimizer tests from the specification, not from the implementation's output. Check the supplied known energy examples; a full energy scan is optional OP04. The smoke check scores a fictional response set, builds its snapshot, computes an exact plan, and checks that practice belongs to allocated topics and excludes diagnostics.
5. Maintain run instructions, test outcomes, the merge queue, and the short demo route. Run the clean-clone check and capture the recording. Release only the reviewed, tested commit; leave unfinished extensions visibly deferred.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min baseline; 30 min initial data and setup; 15 min buffer. | Shared main and first data example. |
| 2 | 30 min reviewed bank/keys/counts; 15 min fictional responses; 15 min buffer. | Core fixtures freeze. |
| 3 | 25 min smoke check; 20 min query/check records; 15 min buffer. | V1 evidence and fixed queries. |
| 4 | 25 min clean-clone check; 20 min run notes; 15 min buffer. | Reproducible core candidate. |
| 5 | 20 min checks and tag; 25 min record/rehearse; 15 min buffer. | Tagged core release and backup. |

Use the checking block for optimizer tests and UI review. Verify the oracle and constraints; return unexpected results to Risi with the failing input.

### Acceptance and explanation

Charlie checks role counts, IDs, choices/keys, sources, diagnostic/practice separation, and fictional response records. Risi reviews the oracle and final release evidence. Hank can explain what the fixtures cover, how a test differs from a demo, how to start from a clean clone, and what the measurements do and do not establish.

In docs/delivery/, retain test outcomes, setup commands, release evidence, the demo script, and recording link. These substantiate the verification and delivery contribution.
