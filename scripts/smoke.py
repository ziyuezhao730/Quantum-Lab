"""Check the production classical pipeline using a fictional student.

Run from the repository root:
    python3 scripts/smoke.py

Exit codes:
    0: Complete classical pipeline passed, including practice retrieval.
    1: A check failed.
    2: Scoring, snapshot, and planning passed; retrieval is unfinished.
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.contracts import PlanRequest
from src.intelligence.assess import score_diagnostic
from src.intelligence.pipeline import load_course, make_snapshot
from src.intelligence.validate import validate_snapshot
from src.optimizer.classical import solve_plan


DATA = ROOT / "data" / "demo"
TOPICS = {"T1", "T2", "T3"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    course = load_course(DATA / "course.json")

    with (DATA / "student_cases.json").open(encoding="utf-8") as file:
        student_cases = json.load(file)

    check(bool(student_cases["cases"]), "No fictional student cases found")
    case = student_cases["cases"][0]

    diagnostic = score_diagnostic(course, case["submitted_choices"])

    expected_scores = case["expected_with_test_weights"]["proficiency"]
    check(
        diagnostic.proficiency == expected_scores,
        "Diagnostic scores differ from the reviewed fictional case",
    )

    request = PlanRequest(
        budget_minutes=case["budget_minutes"],
        proficiency=diagnostic.proficiency,
        requested_solver="exact",
    )

    snapshot = make_snapshot(course, request)

    check(
        snapshot.request == request,
        "Snapshot changed the submitted request",
    )

    restored = validate_snapshot(
        json.loads(snapshot.model_dump_json())
    )
    check(restored == snapshot, "Snapshot JSON round-trip changed its values")

    # Independently verify weights against the specification.
    for topic_id in TOPICS:
        if course.assessment_count == 0:
            expected_weight = 0.5
        else:
            frequency = (
                course.topic_counts[topic_id] / course.assessment_count
            )
            expected_weight = 0.5 + 0.5 * frequency

        check(
            math.isclose(
                snapshot.topic_weights[topic_id],
                expected_weight,
                rel_tol=0.0,
                abs_tol=1e-9,
            ),
            f"Incorrect snapshot weight for {topic_id}",
        )

    plan = solve_plan(snapshot.topic_weights, snapshot.request)

    check(set(plan.allocations) == TOPICS, "Plan has incorrect topic IDs")

    for minutes in plan.allocations.values():
        check(
            type(minutes) is int and minutes in (0, 30, 60),
            "Allocation must be an integer: 0, 30, or 60",
        )

    used_minutes = sum(plan.allocations.values())
    budget = request.budget_minutes

    check(plan.feasible is True, "Planner reported an infeasible result")
    check(used_minutes <= budget, "Plan exceeds the budget")
    check(plan.used_minutes == used_minutes, "Incorrect used-minute total")
    check(
        plan.unused_minutes == budget - used_minutes,
        "Incorrect unused-minute total",
    )
    check(plan.actual_solver == "exact", "Incorrect solver label")
    check(plan.execution_mode == "live", "Incorrect execution label")
    check(
        math.isfinite(plan.elapsed_ms) and plan.elapsed_ms >= 0,
        "Invalid planner duration",
    )
    check(plan.quantum_metrics is None, "Exact plan has quantum metrics")

    # Recalculate utility without calling the optimizer's utility helpers.
    expected_utility = 0.0

    for topic_id, minutes in plan.allocations.items():
        priority = snapshot.topic_weights[topic_id] * (
            1.0 - request.proficiency[topic_id]
        )

        if minutes >= 30:
            expected_utility += priority

        if minutes == 60:
            expected_utility += 0.5 * priority

        if request.proficiency[topic_id] == 1.0:
            check(
                minutes == 0,
                f"Fully proficient topic {topic_id} received study time",
            )

    check(
        math.isclose(
            plan.utility,
            expected_utility,
            rel_tol=0.0,
            abs_tol=1e-8,
        ),
        "Reported utility differs from the independent calculation",
    )

    print(f"Case:        {case['case_id']}")
    print(f"Scores:      {diagnostic.proficiency}")
    print(f"Weights:     {snapshot.topic_weights}")
    print(f"Allocations: {plan.allocations}")
    print(f"Used:        {plan.used_minutes} minutes")
    print(f"Unused:      {plan.unused_minutes} minutes")
    print(f"Utility:     {plan.utility:.6f}")
    print("Scoring, snapshot, and planning checks passed.")

    # Retrieval is currently unfinished. Do not substitute a local algorithm.
    from src.intelligence import rank

    select_questions = getattr(rank, "select_questions", None)

    if not callable(select_questions):
        print("INCOMPLETE: production practice retrieval is not implemented.")
        return 2

    items = select_questions(course, plan, diagnostic.proficiency)

    approved_practice = {
        question.question_id: question
        for question in course.questions
        if question.purpose == "practice"
        and question.review_status == "approved"
    }

    seen_ids = set()
    counts = {topic_id: 0 for topic_id in TOPICS}

    for item in items:
        question_id = item.question_id

        check(question_id not in seen_ids, "Duplicate practice question")
        check(
            question_id in approved_practice,
            f"Question {question_id} is not approved practice",
        )

        question = approved_practice[question_id]

        check(
            plan.allocations[question.topic_id] > 0,
            f"Practice question belongs to unallocated topic {question.topic_id}",
        )

        seen_ids.add(question_id)
        counts[question.topic_id] += 1

    for topic_id in TOPICS:
        expected_count = 2 if plan.allocations[topic_id] > 0 else 0
        check(
            counts[topic_id] == expected_count,
            f"Incorrect practice count for {topic_id}",
        )

    print(f"Practice:    {sorted(seen_ids)}")
    print("SMOKE PASS: production classical pipeline checks passed.")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as error:
        print(f"SMOKE FAIL: {type(error).__name__}: {error}", file=sys.stderr)
        exit_code = 1

    raise SystemExit(exit_code)