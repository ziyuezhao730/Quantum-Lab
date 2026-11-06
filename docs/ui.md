# ExamAce — UI Documentation

## 1. Overview

ExamAce is a Streamlit-based study planning application. Students answer six diagnostic multiple-choice questions, enter their available study time, and generate a personalized study plan.

The UI is implemented in `app.py` and `src/ui/`.

## 2. Student Workflow

1. Open the ExamAce application.
2. Answer six diagnostic questions covering Derivatives, Integrals, and Series.
3. Select a study budget in minutes.
4. Click **Generate Study Plan**.
5. View diagnostic scores, recommended study time, and optimization details.
6. Review practice questions and reveal their answers.
7. Click **Download Snapshot JSON** to save the generated plan.

## 3. Input Validation

The Generate Study Plan button is disabled until all six diagnostic questions have been answered.

The study budget is collected through the UI's numeric input control.

## 4. Planning and Results

The application uses the exact classical optimizer (`solve_exact`) to calculate study-time allocations.

The results interface displays:

- Topic proficiency scores.
- Recommended study time per topic.
- Used and unused study minutes.
- Optimization utility.
- Solver and execution information.
- Practice questions with source references and answer reveals.

## 5. Input Invalidation

ExamAce stores the generated plan in Streamlit session state.

When a student changes a diagnostic answer or the study budget, the previous plan is invalidated.

The old results and Snapshot JSON download button disappear until the student generates a new plan.

## 6. Snapshot JSON

The downloadable snapshot contains:

- Submitted diagnostic answers.
- Study budget.
- Topic proficiency scores.
- Study-time allocations.
- Used and unused minutes.
- Optimization utility and solver metadata.
- Test-mode indicator.

## 7. Current Limitations

The application currently uses fixed test proficiency values rather than calculating proficiency from student answers.

The optimizer itself is real, but the diagnostic scoring integration depends on the Content Intelligence implementation.

Practice questions are loaded from approved demo fixtures and are not yet personalized by student performance.

The current snapshot is explicitly marked with `"test_mode": true`.

## 8. Verification

Manual Streamlit checks completed:

- Six diagnostic questions displayed successfully.
- Study plan generated using the exact optimizer.
- Practice questions and source references displayed.
- Snapshot JSON downloaded and inspected.
- Changing the study budget invalidated the previous results and download button.

Independent fixture validation was also completed with four passing pytest tests.

## 9. Evidence

UI screenshots are stored in `evidence/charlie/`.

## 10. AI Assistance

AI assistance was used to support UI implementation, documentation, and test development. The implemented features were manually verified in Streamlit.