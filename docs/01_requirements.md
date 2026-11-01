# StudyPack Requirements

Shared specification for a five day hackathon

We will build a small application that turns a student's limited study time into a topic plan and a matching practice set. Idea A allocates time; Idea B retrieves questions for the topics receiving that time. Both use the same reviewed course data and student profile. This document defines what must work and how we will check it.

Read this specification once as a team. Then use Document 02 for individual work and Document 03 for the daily schedule and Git commands. These three documents are the complete planning set; decisions belong in issues rather than additional reports.

## 1 Product boundary

The core uses one fictional calculus course, twelve reviewed questions, reviewed counts and excerpts from three authored assessments, and one prepared exercise PDF. Its topics are T1 Derivatives, T2 Integrals, and T3 Series. Each receives 0, 30, or 60 minutes within a total budget of up to 180 minutes. Recommend up to two questions per allocated topic. Separate assessment PDFs are optional.

The student loads reviewed JSON, enters time and confidence, generates a plan, and opens its source-linked practice set. Changing inputs updates both engines. Extract the single prepared PDF outside the app; upload and editing screens are optional.

Use Python and Streamlit for one local application. Keep the bank in JSON and student inputs in session memory. Use pypdf for text extraction, Pydantic for validation, scikit-learn TF-IDF for initial text matching, and Qiskit with a local statevector simulator for the quantum experiment. This stack is a scope decision for thirty team hours.

## 2 Versions and release boundaries

| Version | End of day | Observable result |
| --- | --- | --- |
| V0 Walking skeleton | Day 1 | App loads reviewed sample data, accepts a profile, and calls the agreed interfaces. Placeholders are visibly labelled. |
| V1 Connected classical product | Days 2 and 3 | Exact study plan drives a source-linked practice set over reviewed JSON. One prepared PDF can be extracted separately. |
| V2 Core complete | Day 4 | V1 works and a separate Qiskit experiment compares one fixed study instance with its exact reference. Live quantum integration in the app is optional. |
| V2.1 Demo release | Day 5 | Existing behavior is checked, packaged, and rehearsed. No new features. |

Only the core is assigned. Section 10 lists unassigned extensions anyone may volunteer for. None is required for project integrity, acceptance, or a complete V2 release. Nobody inherits an unclaimed extension or owes extra hours.

Accounts, cloud databases, OCR, community sharing, question generation, automatic marking, multi-course support, and a second quantum question-selection engine remain future directions. A local demo and recorded backup are sufficient deliverables.

## 3 Functional requirements

“Shall” means required for the stated version. An owner delivers the behavior; the independent checker is assigned in Document 02.

| ID | Requirement and acceptance evidence | Version and owner |
| --- | --- | --- |
| FR01 | Load the bundled course without network access. Show three topics and twelve approved questions; all IDs are unique. | V1 Hank |
| FR02 | Extract text from the single prepared exercise PDF, at most three pages and 3 MB, using a script or function. Preserve source and one-based page numbers. No upload screen or general PDF support is required. | V1 Alex |
| FR03 | Parse the supplied topic and difficulty markers into candidate JSON. Validate records; flag missing fields instead of guessing. Hank reviews candidates outside the app and freezes the approved bank. Automatic tagging and a review editor are optional. | V1 Alex |
| FR04 | Accept an integer time budget from 0 to 180 minutes and confidence from 0 to 1 for each topic. Reject missing, nonfinite, or out-of-range inputs with a readable message. | V1 Charlie |
| FR05 | Return topic allocations in thirty-minute blocks, at most sixty minutes per topic and never over budget. Show used and unused time, including any remainder below thirty minutes. | V1 Risi |
| FR06 | Select up to two unique approved questions per allocated topic using the ranking rule in section 6. Show difficulty, matching reason, source, page, and an answer reveal when an approved answer exists. | V1 Alex and Charlie |
| FR07 | Adapt one documented Qiskit example or library ansatz for the fixed AT01 study instance. Run p=1 on a local simulator; validate sampled allocations. A separate runnable script is sufficient. | V2 Risi |
| FR08 | Save one fixed-instance comparison with its inputs, exact and sampled utility, duration, and feasibility. Label live simulation, replay, and failure. The app need not run Qiskit or display the comparison. | V2 Risi |
| FR09 | Give readable messages for invalid JSON, unsupported prepared-PDF input, an empty approved bank, no topic match, and zero study time. Extraction errors may be shown by the preparation script. | V1 Alex and Charlie |
| FR10 | Start from a clean clone using the documented commands; run the smoke check and tests; deliver a release tag and a short demo recording with each person's contribution recorded. | Release Hank |

## 4 Quality and scope controls

The bundled demonstration shall work without API keys or network access after dependencies are installed. Keep uploads in memory or an ignored runtime folder; do not add personal course material or credentials to Git. Use team-authored demo material and retain its source metadata.

Target under two seconds for the classical flow. Measure one bounded quantum attempt separately; do not promise a runtime or accuracy improvement. The app remains usable without the experiment. Any later quantum button is optional and must run only on explicit request.

Display importance as a heuristic score based on supplied assessments. Confidence is self-reported. Neither is a probability of an exam question appearing, a measured learning gain, or a grade forecast.

## 5 Data contracts and integration

Freeze schema version 1 on Day 1. Alex owns src/contracts.py and validates every boundary. Other modules consume these records without renaming fields. Add a field only after posting an example and identifying every consumer in the issue.

| Record | Required fields and meaning |
| --- | --- |
| Topic | topic_id, name, importance in [0,1], evidence list. Each evidence item has source_id, page, and excerpt. IDs are T1, T2, T3. |
| Question | question_id, topic_id, text, difficulty 1/2/3, source_id, page, review_status pending/approved, answer string or null. |
| CourseData | schema_version=1; topics, questions, sources lists; assessment_count integer; topic_counts mapping. Sources have source_id, filename, kind assessment/exercises/authored, and provenance note. |
| PlanRequest | budget_minutes integer [0,180], proficiency mapping every topic ID to a finite number [0,1], requested_solver exact/qaoa. |
| PlanResult | allocations, used_minutes, unused_minutes, utility, feasible, actual_solver, execution_mode, elapsed_ms, fallback_reason or null, warnings list, quantum_metrics or null. |
| QuantumMetrics | qubits, p, shots, seed, feasible_shot_rate, raw_best_utility or null. Present only for a quantum attempt. |

The core app requests exact only; qaoa is used by the separate fixed-instance script. execution_mode is live or cached_replay. If a later extension falls back to exact, populate fallback_reason. Keep the request with the result. Optional fields can be null and do not require building extra behavior.

### Callable interfaces

```python
extract_pdf(file_bytes, source_id) -> list[PageText]
parse_prepared_exercises(pages) -> list[Question]
load_course(json_path) -> CourseData
validate_course(candidate) -> CourseData
solve_plan(course, request) -> PlanResult
select_questions(course, plan, proficiency) -> list[PracticeItem]
```

CourseData.topic_counts maps topic IDs to counts from 0 to assessment_count; the loader computes importance. PageText has source_id, page, text. PracticeItem has question_id, score, reason. PlanResult.allocations maps every topic ID to integer minutes, for example {"T1":0,"T2":60,"T3":30}. quantum_metrics is null or a QuantumMetrics record. Use consistent validation errors and readable warnings. No Streamlit imports inside intelligence or optimizer modules.

### Supported exercise format

The authored exercise PDF uses numbered items such as “1. [T1] [D1] Differentiate x^2.” followed by “Answer: 2x”. D1, D2, and D3 map to difficulty 1, 2, and 3. A source and page are attached during extraction. The parser may flag items without topic or difficulty markers for manual completion; it must not silently invent an answer. Count historical frequency from sources marked assessment, never from the exercise bank.

### How the modules meet

Charlie loads Alex's validated JSON, calls Risi's exact planner, and calls Alex's question selector. Hank supplies the same fixtures. Extraction writes candidates to ignored runtime storage; Hank approves records in data/demo/course.json. The quantum script uses a fixed copy of AT01 and produces its own report. It does not depend on app wiring.

When budget or confidence changes, invalidate the previous plan and practice set. There is no required in-app editor. Keep generated candidates, caches, and student profiles outside tracked demo JSON.

## 6 Planning model and question ranking

The model is deliberately small enough to inspect completely. It is a resource-allocation prototype; the utility is an explicit heuristic, not an estimate of actual learning.

### Topic value and allocation

For each topic i, let f_i be its reviewed assessment count divided by the number of assessments. Hank supplies the counts and source excerpts in reviewed JSON; Alex computes w_i = 0.5 + 0.5 f_i. Count each assessment once per topic. If no evidence is supplied, use w_i = 0.5 with a warning. Extracting these counts automatically from PDFs is optional.

With confidence p_i, define a_i = w_i (1 - p_i). The first thirty-minute block has value a_i; the second has value 0.5 a_i. This simple diminishing-return rule is inspectable and can be replaced after the hackathon.

Let x_i1 and x_i2 be binary choices for those blocks. Require x_i2 <= x_i1 and sum(x_ij) <= B, where B = floor(budget_minutes / 30). Maximize V = sum(a_i x_i1 + 0.5 a_i x_i2). Break utility ties by fewer blocks, then topic ID order. Unused time is allowed.

### Fixed quantum experiment

Use the AT01 fixture only: three unit weights, confidence 0.8/0.2/0.4, and a ninety-minute budget. There are six topic variables and two slack bits for B=3. The formula below is supplied; a reusable converter for arbitrary inputs is optional. Encode unused whole blocks as nonnegative binary slack s.

```text
P = 1 + 1.5 * sum_i(a_i)
E = -V + P * (sum_i,j(x_ij) + s - B)^2
       + P * sum_i[x_i2 * (1 - x_i1)]
```

Minimize E. Any violated integer constraint costs at least P, which exceeds the largest possible utility. The empty plan with slack B is feasible. Expand squared binary terms using x^2=x, and convert x=(1-Z)/2 to an Ising cost. Preserve the constant offset when checking energies.

Adapt the documented QAOA pattern using Qiskit QAOAAnsatz(reps=1) and Statevector. Reuse its initial state and mixer; do not write custom RZ/RZZ/RX construction for the core. Supply the fixed study cost operator and check bit ordering on known allocations. Use one seed, one initial parameter choice, at most thirty classical objective evaluations, and 1,024 final samples. Keep the reference and adapted code changes in the model note.

Keep the best feasible sampled plan by V; do not insert the exact answer into sampled candidates. If the attempt fails, record failure and the exact result separately; do not create app fallback machinery for this experiment. The required goal is one working, explainable comparison, not a tuning framework. This tiny problem is easy classically; no quantum advantage is claimed.

### Question selection rule

For each allocated topic, compare approved question text with that topic's assessment excerpts plus its name. Use TF-IDF cosine similarity, with a topic-name query when excerpts are absent. Set target difficulty to 1 if confidence <0.4, 2 if 0.4 <= confidence <0.7, and 3 otherwise. Rank by 0.7 similarity + 0.3 exact difficulty match; break ties by question ID. Remove exact duplicates after case and whitespace normalization, preserving mathematical symbols. Take at most two per topic, ordering topics by allocated minutes then topic ID. If fewer exist, show the available items and a shortage message. This is text matching; call it semantic search only if an embedding method is actually added and checked.

## 7 Acceptance checks and experiment evidence

Use the following checks as release gates. The automated checks belong to their assigned tester; manual UI checks belong in tests/check_ui.md. Keep the expected outcomes fixed before changing the implementation.

| Check | Fixed input | Expected outcome |
| --- | --- | --- |
| AT01 Hand calculation | Test-only weights all 1; confidence T1=0.8, T2=0.2, T3=0.4; budget 90 | Exact plan T1=0, T2=60, T3=30; utility 1.8 within numerical tolerance. |
| AT02 Budget boundary | Same fixture; budgets 0, 15, 45, and 180 | Never overspend; 0 and 15 allocate no blocks; 45 uses at most 30 minutes; each topic <=60. |
| AT03 Personalization | AT01 but T2 confidence becomes 0.9 | Exact plan T1=30, T2=0, T3=60; utility 1.1. Practice set contains T1 and T3 only. |
| AT04 Data quality | Repeated question ID, unknown topic, missing source page, malformed numeric value | Validator identifies the bad record. Pending questions are not retrieved. |
| AT05 Retrieval | Six frozen queries with acceptable question IDs in retrieval_cases.json | Record actual hit@2 and wrong-topic count. Target at least 5/6 hits and zero wrong-topic recommendations. |
| AT06 Prepared PDF | Supplied numbered exercise PDF and one unsupported or malformed input | Candidate JSON preserves markers and page references; unsupported input produces a readable message. Wider format coverage is optional. |
| AT07 Fixed quantum case | AT01 plus known empty, optimal, and constraint-violating allocations | Check energy and bit decoding on those examples; record one real simulator attempt and a feasible sampled plan. Exhaustive model scans are optional. |
| AT08 Honest results | Fixed experiment report, saved replay, changed app confidence | Report identifies its fixed inputs and execution mode; it is not presented as the current app plan. Changing app inputs clears stale practice output. |
| AT09 Reproducibility | Fresh clone on a second machine or clean environment | Setup, tests, smoke check, and demo launch succeed using HOW-TO-RUN.md. |

AT01 and AT03 deliberately inject unit weights into the test model; the displayed demo weights still come from the assessment-counting rule. Comparing floating-point utility should use a tolerance such as 1e-8.

### Required experiment record

Record one run of AT01 with seed 7, p=1, and 1,024 samples. Save the input, adapted-example reference, parameter settings, qubit count, raw sampled utility, exact utility 1.8, feasibility, and elapsed time. If no feasible sample exists, use null for sampled utility and state the failure. This is a small demonstration, not a statistical benchmark or a claim about student grades.

The nine-run benchmark, multiple starts, tuning comparisons, and exhaustive QUBO/Ising scans belong only to optional item OP04. They are not release gates. A core feature is complete after its listed checks pass, even if nobody claims those additional experiments.

## 8 Release checklist and demonstration

A feature is done when its requirement is met, its assigned check passes, another person reviews it, the pull request is merged, and the board shows its true state. A component can be complete while a stretch feature remains deferred.

A complete V2 consists of the usable V1 app, prepared-format extraction, the single fixed Qiskit comparison, and the required check evidence. A separate quantum script satisfies FR07 and FR08. Every item in section 10 may remain unclaimed and unfinished without weakening that completion status. If a core quantum run does not work, report the release as V1 and state that limitation; optional work cannot replace a core check.

### Four minute demo route

1. Hank introduces the student problem and loads the reviewed fictional course, naming the data scope.
2. Alex shows extraction from the prepared PDF and traces an approved question and its importance evidence in JSON.
3. Charlie enters a ninety-minute budget and confidence values, generates a classical plan, and opens the linked practice set.
4. Risi opens or runs the separate fixed-instance Qiskit comparison, identifies its inputs, and explains the exact reference and one limitation.
5. Charlie changes one confidence value and shows the refreshed plan and questions. Hank closes with the tested scope and release evidence.

Aim for roughly forty-five seconds per speaker, with transition time. Do not add slides unless the submission rules require them. Rehearse on the actual laptop with a recorded fallback available and visibly identified.

### Evidence to keep

- Merged issues and pull requests showing each person's implementation, testing, and review contributions.
- Reviewed assessment counts and excerpts, the prepared exercise PDF, approved JSON, and the small gold-query file.
- One fixed quantum run report with its inputs, test outcomes, and one screenshot of the working app. A larger benchmark and custom circuit drawing are optional.
- HOW-TO-RUN.md, the release tag, a brief demo script, and a short recording. Store large video outside Git if necessary and place its link in the delivery notes.

Use only completed, personally understood contributions in resume statements. Numbers must come from these artifacts. It is useful to explain why exact enumeration is the sensible production solver for this tiny instance and why QAOA is an experiment.

## 9 Design references

- Shared product discussion: https://chatgpt.com/share/6ae78927-ee70-83ea-bac8-cbb44a363eea
- IBM QAOA tutorial describes the alternating cost and mixer workflow: https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm
- IBM QAOAAnsatz supplies the reusable circuit template: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz
- IBM Statevector API supports local circuit simulation and sampling: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector
- pypdf text extraction documents the limits of image-only PDFs: https://pypdf.readthedocs.io/en/stable/user/extract-text.html
- scikit-learn text feature documentation supports the TF-IDF baseline: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction

Consult references while implementing; explanations belong inside the scheduled work blocks.

## 10 Optional work that anyone may claim

All items below are unassigned and outside the required scope. They are not required for project integrity, core acceptance, or a complete V2 release. No person is expected to complete them, and an unclaimed item is not a missing contribution. The main app, demo, and core checks must work with every optional item absent.

### How to claim an extension

After completing your core slice and its checks, voluntarily assign yourself one optional issue on the board. Include the extension ID, intended output, a personal time limit, and any files you need to borrow. Coordinate with the existing file owner; a claim does not transfer ownership of shared contracts. Keep optional work in a separate branch and PR. Anyone can claim any item; none is reserved for a named workstream.

Use only genuinely spare or voluntary time. Preserve the daily integration buffer. Optional work does not add an obligation to another member, including a reviewer; arrange review only when core work permits. At the time limit, stop and leave the issue deferred if unfinished. Do not merge a partial extension that breaks the baseline. The Thursday feature freeze still applies.

| Extension | Additional outcome beyond the core | Claim status |
| --- | --- | --- |
| OP01 Wider document import | Multiple PDFs, broader textbook layouts, automatic topic tags or counts, and an upload/review editor. The prepared-format script remains the baseline. | Unassigned |
| OP02 Live quantum planning | Rebuild the cost for arbitrary budgets and profiles and connect Qiskit to the app, including cache invalidation and explicit fallback labels. | Unassigned |
| OP03 Custom quantum circuit | Construct cost and mixer gates directly, compare them with the library ansatz, and explain coefficients and offsets. | Unassigned |
| OP04 Extended evaluation | Three profiles times seeds 7, 11, and 23; multiple starts; full QUBO/Ising scans including offsets; and a comparison chart. Keep raw and fallback results separate. | Unassigned |
| OP05 AI extraction adapter | One provider converts text into candidate records; the existing validator, source references, and manual approval still apply. | Unassigned |
| OP06 Embedding retrieval | Compare an embedding method with TF-IDF on frozen queries; report actual results and keep the working baseline. | Unassigned |
| OP07 More demonstration material | Extra reviewed questions, separately typeset assessment PDFs, additional query cases, or additional failure fixtures. | Unassigned |
| OP08 Presentation polish | Custom styling, extra visualizations, exports, circuit artwork, or an enhanced recording. The plain working demo is sufficient. | Unassigned |

These are separate projects of varying effort, not promised one-evening tasks. Do not begin several at once. Accounts, public community sharing, cloud databases, OCR, and adaptive learning remain future directions outside this five-day plan.
