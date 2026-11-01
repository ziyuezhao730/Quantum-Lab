# StudyPack Team Work Packages

Individual requirements and handoff checks

Risi owns the decision engine, Alex content intelligence, Charlie the student workflow, and Hank verification and delivery. Read this page and your own package. Use Document 01 for shared contracts.

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

Hank creates the common skeleton and ignored-file rules in the first fifteen minutes of Day 1. During that time, Risi works through AT01, Alex checks the contract example, and Charlie sketches the single-screen flow. Everyone then clones the same baseline and branches from main. A component may use a clearly marked stub until its dependency lands.

## 4 Risi work package

### Objective and owned outputs

Deliver the exact study planner and one separate fixed-instance quantum experiment for FR05, FR07, and FR08. Reusing a documented circuit template is the intended core approach.

Own src/optimizer/model.py, classical.py, and quantum_demo.py; docs/model.md; and evidence/risi/. Own tests/test_intelligence.py as Alex's independent checker. Hank owns tests/test_optimizer.py. Do not edit the UI, fixtures, or shared contracts directly.

### Required steps

1. Implement block utilities, feasibility checks, and the twenty-seven-allocation exact reference. Use AT01's hand calculation to verify the result and the tie rule.
2. Use the supplied QUBO formula for one fixed AT01 case. Explain its value and penalty terms; check a few known allocations and bit ordering.
3. Adapt one documented Qiskit example using its library QAOA ansatz and local simulator. Reuse the circuit template and mixer. Do not build a custom gate sequence or general solver framework.
4. Produce one separate runnable experiment and a comparison report with the fixed input, exact answer, sampled result, and limitations. App wiring is optional OP02; extended benchmarking is OP04.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min oracle and contract; 30 min exact-solver first pass; 15 min buffer. | Inspectable allocator, or explicit stub and blocker. |
| 2 | 30 min finish exact checks; 15 min fixed cost example; 15 min buffer. | Exact result ready for V1. |
| 3 | 45 min adapt a documented Qiskit example to the fixed cost; 15 min buffer. | One bounded experiment attempt. |
| 4 | 25 min finish run and decode; 20 min save and explain comparison; 15 min buffer. | Fixed-instance quantum evidence. |
| 5 | 25 min core fixes; 20 min rehearse and finalize note; 15 min buffer. | Verified contribution, no optional quota. |

Keep the additional fifteen-minute check block and fifteen-minute stand-up. If adaptation is blocked, share the failing example promptly; do not add custom features or promise overtime.

### Acceptance and explanation

Hank checks AT01, AT02, and the known examples in AT07. Alex reviews the fixed-input comparison and result labels. Explain the objective, constraints, library template, sampled feasibility, and why this experiment demonstrates no speedup. Exhaustive energy scans and custom gates are optional.

In docs/model.md, retain the hand calculation, adapted-example reference, specific changes, one actual defect and fix, and the single run report. These support a precise optimization resume claim without implying an original quantum framework.

## 5 Alex work package

### Objective and owned outputs

Deliver a validated question bank, retrieval, and extraction from one prepared PDF for FR02, FR03, and FR06. The core consumes reviewed JSON and explicit markers rather than interpreting arbitrary documents.

Own src/contracts.py; src/intelligence/pdf_extract.py, validate.py, pipeline.py, and rank.py; docs/pipeline.md; and evidence/alex/. Own tests/check_ui.md as Charlie's independent checker. Risi owns tests/test_intelligence.py. Charlie alone edits application screens.

### Required steps

1. Validate the reviewed JSON and share one passing example. Reject duplicate IDs, unknown topics, missing provenance, and invalid numbers. Keep approved and pending records distinct.
2. Build retrieval over the approved bank using topic filtering, TF-IDF, difficulty matching, duplicate suppression, and the fixed tie rule. Consume the exact plan's allocations.
3. Extract only the supplied numbered-PDF format and its explicit topic/difficulty markers. Write candidates to runtime/; Hank performs manual approval outside the app. Do not add automatic tagging, broad textbook parsing, or an editor.
4. Compute importance from reviewed assessment counts in JSON. Check the six frozen queries and preserve actual results. Additional extraction methods and embeddings belong to the unassigned backlog.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min contract example; 30 min validation and JSON loader; 15 min buffer. | Valid shared data boundary. |
| 2 | 45 min topic filtering and first ranking pass; 15 min buffer. | Matching questions from the exact plan. |
| 3 | 30 min prepared-PDF parser; 15 min reviewed-count calculation; 15 min buffer. | Traceable preparation path. |
| 4 | 25 min query and error checks; 20 min fixes and evidence; 15 min buffer. | Core pipeline checked. |
| 5 | 25 min core fixes; 20 min trace rehearsal and note; 15 min buffer. | Verified contribution, no optional quota. |

Use the separate check block for Charlie's UI procedure and Risi's result review. If parsing is blocked, retain the reviewed JSON flow and raise the specific failing prepared example at stand-up.

### Acceptance and explanation

Risi checks AT04, AT05, and the supplied-format extraction in AT06. Charlie reviews the trace from a source record to a recommended question. Explain validation, lexical ranking, the effect of a wrong tag, and how changing the plan changes the practice set.

In docs/pipeline.md, retain one prepared-PDF-to-record example, the ranking equation, actual query results, and one defect and fix. The resume claim is the validated preparation and retrieval pipeline; broader AI extraction is claimed only if voluntarily added and shipped.

## 6 Charlie work package

### Objective and owned outputs

Deliver the student-facing workflow for FR04 and the presentation parts of FR06 and FR09. A student should understand the plan, find the associated questions, and recognize whether a result is live, replayed, or a fallback.

Own app.py, src/ui/inputs.py, src/ui/results.py, docs/ui.md, and evidence/charlie/. Own tests/test_fixtures.py as Hank's independent checker. Alex writes tests/check_ui.md. Do not implement ranking rules or optimizer math inside the UI.

### Required steps

1. Build one Streamlit page with reviewed demo loading, study-time input, and three confidence controls. Upload and review screens are optional OP01. Prefer standard controls and a small table over custom styling.
2. Call the agreed interfaces. Show allocations, total and unused time, explanations, and practice questions. Reveal an answer only on request, and show “answer unavailable” when it is null.
3. Add one explicit planning button. Invalidate the plan and questions when inputs change. The separate quantum script requires no app controls, background jobs, or quantum cache.
4. Label the app result as exact classical optimization. A fixed quantum report can be opened separately; it is not a live result for the current app profile.
5. Give readable input and empty-state messages. Keep standard controls and a working demo-data route; custom graphics and exports are optional.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min sketch; 30 min inputs and demo view; 15 min buffer. | V0 accepts a profile. |
| 2 | 45 min wire exact plan and practice display; 15 min buffer. | First V1 flow. |
| 3 | 25 min state invalidation; 20 min answer/source labels; 15 min buffer. | V1 checked end to end. |
| 4 | 25 min error/empty states; 20 min usability fixes; 15 min buffer. | Core screens checked. |
| 5 | 20 min core fixes; 25 min rehearsal and note; 15 min buffer. | Verified release contribution. |

Use the checking block to check fixture records and review Alex's pipeline changes. Trace the input/output examples and reproduce any unclear behavior with the owner.

### Acceptance and explanation

Alex checks AT03, AT08, the zero-time screen, and missing-answer behavior. Hank reviews the flow from a clean launch. Charlie can explain where session state is used, when cached output becomes stale, how one form triggers the planning and retrieval calls, and how the user sees an input or planning failure.

In docs/ui.md, record the screen flow, input rules, invalidation rule, and a screenshot tied to the release. A completed contribution can be described as building an interactive study-planning and practice workflow, including state handling and clear experiment results.

## 7 Hank work package

### Objective and owned outputs

Deliver reproducible data, independent verification, and a dependable demo for FR01 and FR10. The release must be runnable by someone other than its implementers and backed by traceable checks.

Own data/demo/, scripts/smoke.py, requirements.in, requirements.txt, .gitignore, README.md, HOW-TO-RUN.md, docs/decisions.md, docs/delivery/, and evidence/hank/. Own tests/test_optimizer.py as Risi's independent checker. Charlie owns tests/test_fixtures.py. Each member owns their own stand-up note.

### Required steps

1. Create the shared repository baseline and placeholders from Document 03. Exclude credentials, runtime uploads, caches, and environments. Record the agreed Python version and lock the working dependencies from a clean environment.
2. Create twelve small original questions, four per topic, including approved answers and difficulty values. Supply reviewed counts and excerpts for three short authored assessments, plus one prepared exercise PDF with explicit markers. Separate assessment PDFs are optional OP07. AI may draft them; manually verify every displayed question and answer, source page, and topic tag. Avoid complex typesetting.
3. Prepare the exact-solver oracle, six frozen retrieval queries with acceptable IDs, and malformed records. Keep test-only weights separate from actual assessment-derived demo weights.
4. Write optimizer tests from the specification, not from the implementation's output. Check the supplied known energy examples; a full energy scan is optional OP04. The smoke check loads data, computes an exact plan, and verifies that retrieved questions belong to allocated topics.
5. Maintain run instructions, test outcomes, the merge queue, and the short demo route. Run the clean-clone check and capture the recording. Release only the reviewed, tested commit; leave unfinished extensions visibly deferred.

### Daily implementation budget

| Day | Sixty minute work slice | Handoff |
| --- | --- | --- |
| 1 | 15 min baseline; 30 min initial data and setup; 15 min buffer. | Shared main and first data example. |
| 2 | 30 min finish reviewed bank/counts; 15 min prepared PDF; 15 min buffer. | Core fixtures freeze. |
| 3 | 25 min smoke check; 20 min query/check records; 15 min buffer. | V1 evidence and fixed queries. |
| 4 | 25 min clean-clone check; 20 min run notes; 15 min buffer. | Reproducible core candidate. |
| 5 | 20 min checks and tag; 25 min record/rehearse; 15 min buffer. | Tagged core release and backup. |

Use the checking block for optimizer tests and UI review. Verify the oracle and constraints; return unexpected results to Risi with the failing input.

### Acceptance and explanation

Charlie checks counts, IDs, sources, answers present where expected, and query records. Risi reviews the oracle and final release evidence. Hank can explain what the fixtures cover, how a test differs from a demo, how to start from a clean clone, and what the measurements do and do not establish.

In docs/delivery/, retain test outcomes, setup commands, release evidence, the demo script, and recording link. These substantiate the verification and delivery contribution.
