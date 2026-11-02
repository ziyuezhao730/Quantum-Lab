# ExamAce Requirements

Shared specification for a five day hackathon

ExamAce uses a short diagnostic and a student's available time to produce a personalized study plan and a source-linked practice set. Idea A allocates time; Idea B retrieves practice for the topics receiving that time. A separate Qiskit experiment compares QAOA with the exact classical solver using the same saved student profile.

Read this specification once as a team. Document 02 assigns individual work; Document 03 gives the daily schedule and Git commands. Decisions belong in issues rather than additional reports.

## 1 Product boundary

Use one fictional calculus course with T1 Derivatives, T2 Integrals, and T3 Series. Keep twelve reviewed questions: two diagnostic multiple-choice questions and two practice questions per topic. Also supply reviewed topic counts and excerpts from three short authored assessments. No additional question bank or PDF is required.

The student answers six diagnostic questions, enters an integer time budget from 0 to 180 minutes, and presses one planning button. The app scores each topic, computes an exact plan, and recommends up to two practice questions per allocated topic. Each topic receives 0, 30, or 60 minutes. No accounts, names, or student database are needed.

Download the resulting profile as JSON for the separate quantum script. It uses that profile's scores, weights, and budget rather than a hard-coded demonstration student. One real simulator comparison is required; a live quantum button and a multi-profile benchmark are optional.

Use Python, Streamlit, Pydantic, scikit-learn TF-IDF, NumPy, SciPy, Qiskit, and pytest. Student answers stay in session memory or ignored runtime storage. JSON loading replaces required PDF extraction. This exchanges scope within thirty team hours; it does not add overtime.

## 2 Versions and release boundaries

| Version | End of day | Observable result |
| --- | --- | --- |
| V0 Walking skeleton | Day 1 | Reviewed data and agreed interfaces load; a visibly labelled sample profile reaches the planner. |
| V1 Personalized classical product | Days 2 and 3 | Six answers produce topic scores, an exact allocation, and separate targeted practice. A matching profile snapshot downloads. |
| V2 Core complete | Day 4 | A separate Qiskit script compares one exported student profile with its exact classical reference. |
| V2.1 Demo release | Day 5 | Existing behavior is checked, packaged, and rehearsed. No new features. |

Only the core is assigned. Section 10 contains unassigned extensions. None is required for project integrity, acceptance, or a complete V2 release; nobody inherits an unclaimed extension.

PDF import, generative assessment, free-text marking, accounts, OCR, cloud services, multi-course support, and learning-outcome studies are outside the core. The diagnostic uses answer-key checking. TF-IDF supports retrieval, not assessment. Describe the system as diagnostic-based personalization; do not claim AI-driven assessment, proven learning gains, or quantum advantage.

## 3 Functional requirements

An owner delivers the behavior; Document 02 assigns a different checker and reviewer. Preserve the requirement IDs in issues, but update old issue descriptions to these definitions.

| ID | Requirement and acceptance evidence | Version and owner |
| --- | --- | --- |
| FR01 | Load three topics and twelve approved questions offline: six diagnostic and six practice, two of each per topic. IDs are unique and sources are traceable. | V1 Hank |
| FR02 | Score six submitted choice IDs against the reviewed diagnostic key. Return each topic's fraction correct; reject incomplete or invalid submissions. | V1 Alex |
| FR03 | Validate reviewed JSON, question roles, diagnostic choices, answer keys, sources, and counts. Build a validated snapshot containing the current request and topic weights. | V1 Alex |
| FR04 | Provide one screen with six unanswered choice controls and an integer budget from 0 to 180. Show topic scores, their limited meaning, and a profile download after submission. | V1 Charlie |
| FR05 | Find the exact best feasible allocation in thirty-minute blocks, at most sixty minutes per topic. Show used and unused time. | V1 Risi |
| FR06 | Retrieve up to two unique approved practice questions per allocated topic. Exclude all diagnostic questions. Show difficulty, matching reason, source, page, and available answer reveals. | V1 Alex and Charlie |
| FR07 | Construct the supplied cost model from a validated exported profile. Adapt a documented Qiskit ansatz, run p=1 locally, and validate sampled plans. | V2 Risi |
| FR08 | Save one comparison using identical scores, weights, and budget for both solvers. Record utility, feasibility, duration, settings, and whether results are live simulation or replay. | V2 Risi |
| FR09 | Show readable errors for invalid course data, incomplete answers, invalid budget, empty practice, and zero study time. Clear stale results when inputs change. | V1 Alex and Charlie |
| FR10 | Document clean-clone setup, run checks, and deliver a reviewed release tag and short recording with each person's contribution recorded. | Release Hank |

## 4 Quality and scope controls

Work without API keys or network access after installation. Use team-authored material. Keep credentials, actual student profiles, and generated runtime files out of Git. A deliberately fictional example may be retained as experiment evidence.

Target under two seconds for the classical flow. Bound the separate quantum attempt as specified in section 7; measure its runtime without promising an improvement. A failed experiment must not stop the classical app.

Two questions per topic provide only a coarse initial signal: scores are 0, 0.5, or 1. Display “Initial topic score from two questions”. Importance is a heuristic from supplied assessment counts. Neither quantity predicts grades, establishes mastery, or measures learning gain.

## 5 Data contracts and integration

Freeze schema version 1 on Day 1 before implementation. Alex owns src/contracts.py; changes require an issue example and agreement from consumers. If an older schema has already been implemented, coordinate a version bump instead of silently reusing its version number.

| Record | Required fields and meaning |
| --- | --- |
| Topic | topic_id, name, importance in [0,1], evidence list containing source_id, page, excerpt. IDs are T1, T2, T3. |
| Question | question_id, topic_id, text, difficulty 1/2/3, purpose diagnostic/practice, source_id, page, review_status pending/approved, answer string or null. Diagnostic items also require choices mapping choice IDs to text and correct_choice matching a choice ID. |
| CourseData | schema_version=1; topics, questions, sources; assessment_count integer; topic_counts mapping. Sources have source_id, filename or authored label, kind, provenance note. |
| DiagnosticResult | submitted_choices mapping six question IDs to valid choice IDs; proficiency mapping all topic IDs to fraction correct. Never accept a client-supplied score without checking answers. |
| PlanRequest | budget_minutes integer [0,180]; proficiency mapping T1/T2/T3 to finite numbers [0,1]; requested_solver exact/qaoa. |
| ProfileSnapshot | schema_version=1; profile_source=diagnostic; request containing the submitted budget and computed proficiency; topic_weights mapping all topic IDs to finite numbers [0.5,1]. No personal identity fields. |
| PlanResult | allocations, used_minutes, unused_minutes, utility, feasible, actual_solver, execution_mode, elapsed_ms, warnings list, quantum_metrics or null. |
| QuantumMetrics | qubits, p, shots, seed, feasible_shot_rate, raw_best_utility or null. Present only for the quantum attempt. |

The app requests exact only. The script copies the snapshot request and changes requested_solver for each run; scores, weights, and budget remain identical. execution_mode is live or cached_replay. A replay always carries its original profile. Do not substitute an exact answer for a quantum sample.

### Callable interfaces

```python
load_course(json_path) -> CourseData
validate_course(candidate) -> CourseData
score_diagnostic(course, submitted_choices) -> DiagnosticResult
make_snapshot(course, request) -> ProfileSnapshot
validate_snapshot(candidate) -> ProfileSnapshot
solve_plan(topic_weights, request) -> PlanResult
select_questions(course, plan, proficiency) -> list[PracticeItem]
```

PracticeItem contains question_id, score, reason. Allocations map all topic IDs to integer minutes. No intelligence or optimizer module imports Streamlit. Alex owns scoring and serialization; Charlie calls those functions and displays their results; Risi consumes the same validated weights and request.

Charlie uses ordinary Streamlit widgets with change callbacks and no initial choice selection; avoid st.form, which batches changes. A single planning button submits the inputs. On submit, Alex's scorer validates all six answers; the app builds the request, solves, retrieves, and offers snapshot JSON through one standard download button. Save it as runtime/student_profile.json for the command in Document 03. This is a file handoff, not a quantum service.

Any changed answer or budget clears the previous plan, practice, and download until resubmission. Keep two fictional response sets in data/demo/student_cases.json so the same flow can be checked without real student data.

## 6 Personalization and optimization model

The utility is an explicit study-priority heuristic, not a prediction of learning. Use the same formula for both solvers.

### Diagnostic scoring and practice

For topic i, p_i is correct diagnostic answers divided by two. Use only its two approved diagnostic items; do not blend in self-reported confidence or build a history model. A missing answer is an incomplete submission, not an incorrect answer. One changed response need not always change the allocation; check the deliberately selected contrasting cases below.

Validate exactly two diagnostic and two practice items per topic. Diagnostic items have at least two distinct choices and one valid key; verify the mathematical answer manually. Keep diagnostics out of recommended practice. Practice answers may be null and must be labelled unavailable.

For each allocated topic, compare its approved practice text with the topic's authored assessment excerpts plus topic name using TF-IDF cosine similarity. Use the topic name if excerpts are absent. Target difficulty is 1 for p_i<0.4, 2 for 0.4<=p_i<0.7, and 3 otherwise. Rank by 0.7 similarity + 0.3 exact difficulty match; break ties by question ID. Deduplicate normalized text while preserving mathematical symbols. Return at most two per topic, ordered by allocated time then topic ID. Show available items and a shortage message when necessary.

### Topic values and exact allocation

Let f_i be the number of supplied assessments mentioning topic i divided by assessment_count. Count each assessment once per topic. Compute w_i = 0.5 + 0.5 f_i from reviewed counts; if there are no assessments, use 0.5 with a warning. Automatic extraction is optional.

Define a_i = w_i(1-p_i). The first thirty-minute block has value a_i; the second has value 0.5a_i. For binary block choices x_i1 and x_i2, maximize V = sum_i(a_i x_i1 + 0.5a_i x_i2), subject to x_i2<=x_i1 and sum(x_ij)<=B, where B=floor(budget_minutes/30). At most two blocks per topic are available. Break utility ties by fewer blocks, then lexicographically prefer more blocks for earlier topic IDs.

Enumerate all 27 topic allocations for the exact solution. Unused time and a sub-thirty-minute remainder are allowed. At p_i=1, the exact solver assigns no block to that topic under the fewer-blocks tie rule.

### Contrasting student examples

With the same ninety-minute budget and test-only unit weights, Student A scores T1=1, T2=0, T3=0.5. The exact plan is T1=0, T2=60, T3=30, utility 2.0. Student B scores T1=0, T2=1, T3=0.5; the plan becomes T1=60, T2=0, T3=30, also utility 2.0. The topic sets in their practice differ. Hank supplies fictional choice IDs that produce these scores.

These are tests of personalized behavior under specified inputs. Actual demo weights use the reviewed counts; calculate the exact reference anew rather than copying 2.0 into an experiment report.

## 7 Quantum experiment

### Supplied cost construction

Use the three-topic model only. Keep three slack bits for every allowed budget: s=y0+2y1+4y2. Six topic bits plus three slack bits give nine qubits. For the exported profile, compute a_i, B, and the following energy:

```text
P = 1 + 1.5 * sum_i(a_i)
E = -V + P * (sum_i,j(x_ij) + s - B)^2
       + P * sum_i[x_i2 * (1 - x_i1)]
```

Order bits z=(x11,x12,x21,x22,x31,x32,y0,y1,y2). Use c=(1,1,1,1,1,1,1,2,4) and v=(a1,0.5a1,a2,0.5a2,a3,0.5a3,0,0,0). The binary polynomial is C+sum L_j z_j+sum_{j<k} Q_jk z_j z_k, with:

```text
C = P*B^2
L_j = P*c_j^2 - 2*P*B*c_j - v_j + P*is_second_block(j)
Q_jk = 2*P*c_j*c_k - P*is_same_topic_block_pair(j,k)
```

Convert z_j=(1-Z_j)/2: the Z_j coefficient is -L_j/2-sum_{k!=j}Q_jk/4; the Z_j Z_k coefficient is Q_jk/4; the constant offset is C+sum L_j/2+sum Q_jk/4. Include every pair once. Preserve the offset for energy checks. Bit j maps to Qiskit qubit j; reverse displayed bitstrings before interpreting them as z in index order.

This supplied formula covers only the agreed small model, avoiding a general converter. Every violated integer constraint costs at least P, greater than the maximum possible V. A feasible empty plan has s=B. Feasibility checking includes slack equality and block ordering, not just the displayed time total.

### One bounded comparison

Adapt QAOAAnsatz(reps=1) and Statevector with the generated cost operator. Reuse its initial state and mixer. Use seed 7, one initial parameter choice, at most thirty classical objective evaluations, and 1,024 final samples. Optimize expected energy, then choose the best feasible sampled plan by V, applying the same tie rule among those samples. Custom gates, multiple starts, and a tuning framework are optional.

Run once on a diagnostic-exported fictional profile. Save the entire snapshot, code commit, reference, parameters, qubit count, exact utility, best feasible sampled utility, feasible-shot rate, absolute utility gap, and durations of the exact solve and complete QAOA attempt including operator construction. If no feasible sample exists, record null and failure; fix within the allocated time before calling V2 complete. Never silently insert the exact solution.

A single simulated run is a case study. Report solution quality and constraint satisfaction; do not infer statistical reliability, hardware runtime, speedup, or student learning gains. Extended evaluation remains optional OP04.

## 8 Acceptance and release evidence

The assigned checker writes the automated check or concrete manual procedure. Keep expected outcomes fixed before changing implementation.

| Check | Input | Expected outcome |
| --- | --- | --- |
| AT01 Model oracle | Unit weights; p=(0.8,0.2,0.4); budget 90 | Exact allocation (0,60,30), utility 1.8 within 1e-8. Model-only test; these scores need not come from the six-item diagnostic. |
| AT02 Budget limits | Oracle with budgets 0,15,45,180 | No overspend; 0 and 15 allocate no blocks; 45 uses at most 30; every topic <=60. |
| AT03 Personalization | Fictional Student A and B answers from section 6; unit weights | Scores and allocations match section 6; practice topic sets differ; no diagnostic item appears. |
| AT04 Data validation | Duplicate ID, wrong role counts, missing source, invalid diagnostic key, malformed number | Reject the bad record with its reason. Pending items never become diagnostic or practice output. |
| AT05 Retrieval | Six frozen cases naming a target topic, proficiency, and acceptable top question IDs | At least 5/6 hit@1 and no wrong-topic or diagnostic recommendations. Record actual results. |
| AT06 Diagnostic and export | All correct, all wrong, partial, invalid choice; then submit a valid profile | Scores 1 or 0 as appropriate; incomplete/invalid answers rejected. Downloaded scores, weights, and budget match the submitted plan. |
| AT07 Quantum model | Empty, known-optimal, and ordering-violating bit assignments; budgets 0,3,6 blocks | Binary and Ising energies including offset agree. Valid examples pass decoding; invalid examples fail. One exported-profile simulation yields a feasible sampled plan. |
| AT08 State and report | Change answer/budget after submit; compare saved snapshot with report | Clear old app output/download. Report retains its original inputs and labels simulation/replay. Both solvers use identical problem data. |
| AT09 Reproducibility | Fresh clone or clean environment on a second machine | Setup, tests, smoke, app launch, profile export, and script command work using HOW-TO-RUN.md. |

AT01 and AT03 inject unit weights into the test model only. Core V1 requires the personalized classical workflow, export, and its checks. Core V2 also requires the actual Qiskit comparison and its checks. Use V1 if the quantum experiment is unfinished. No optional feature substitutes for a failed core check.

## 9 Demonstration and release

### Four minute demonstration

1. Hank introduces the student problem and the reviewed fictional course.
2. Charlie submits six answers and a budget, shows initial topic scores, and downloads the snapshot. Preselect the fictional demonstration responses before the timed presentation.
3. Alex traces an answer through scoring, validation, and practice retrieval. Show the contrasting second student's different plan using the same course and budget.
4. Risi opens the comparison for the first saved profile and explains the objective, constraints, exact reference, and simulator limitation. A labelled replay avoids waiting during the presentation.
5. Hank closes with the checked release and known scope. Allow roughly forty-five seconds per speaker plus transitions.

Keep merged PRs, reviewed fixtures, actual test results, a fictional-profile comparison, setup instructions, release tag, screenshot, and short recording. Each person records their completed and understood contribution. No separate learning phase or additional report set is required.

Suggested project description: ExamAce uses a short diagnostic and available study time to produce a personalized study plan and targeted practice. We investigate QAOA through Qiskit simulation and compare it with an exact classical baseline on one student-specific allocation problem. The experiment evaluates our heuristic objective, not actual learning outcomes.

### Design references

- IBM QAOA tutorial: https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-optimization-algorithm
- Qiskit QAOAAnsatz: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QAOAAnsatz
- Qiskit Statevector: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector
- scikit-learn text features: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
- Original product discussion: https://chatgpt.com/share/6ae78927-ee70-83ea-bac8-cbb44a363eea

Consult references while implementing; explanations belong within the scheduled work blocks.

## 10 Optional work that anyone may claim

Every item below is unassigned and outside the required scope. None is needed for project integrity, core acceptance, or a complete V2 release. An unclaimed item is not a missing contribution. All core code, checks, and the demo work with every extension absent.

After core checks pass, anyone may voluntarily claim one issue. State its output, personal time limit, affected files, and extension ID. Coordinate borrowed files with their owner. Use a separate branch and PR. Do not impose extra time on a reviewer or another owner. Preserve the buffer and feature freeze; stop and defer when the time limit is reached.

| Extension | Additional outcome beyond the core | Claim status |
| --- | --- | --- |
| OP01 Document import | Extract one prepared marked PDF; optionally extend formats, topic tagging, or upload/review screens. PDF extraction is no longer required. | Unassigned |
| OP02 Live quantum planning | Connect Qiskit to the app with explicit execution, cache invalidation, result labels, and fallback handling. Saved-profile script remains sufficient. | Unassigned |
| OP03 Custom quantum circuit | Construct gates directly and compare with the library ansatz; explain coefficients and offsets. | Unassigned |
| OP04 Extended evaluation | More student profiles, seeds 7/11/23, multiple starts, exhaustive model scans, or comparison charts. | Unassigned |
| OP05 AI assessment or extraction | Add and evaluate an AI-based assessment or text extraction method. Preserve reviewed keys, provenance, and the working baseline. | Unassigned |
| OP06 Embedding retrieval | Compare embeddings with TF-IDF on frozen queries and report actual results. | Unassigned |
| OP07 More material | Additional reviewed questions, assessment PDFs, diagnostic items, or failure cases. | Unassigned |
| OP08 Presentation polish | Custom styling, visualizations, additional exports, artwork, or an enhanced recording. | Unassigned |

These are projects of varying effort, not promised one-evening tasks. No optional quota is assigned. Accounts, public sharing, cloud databases, OCR, adaptive histories, and learning-outcome studies remain future directions outside this five-day plan.
