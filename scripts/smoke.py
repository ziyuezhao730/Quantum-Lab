"""End-to-end smoke check for the ExamAce core (FR01 + FR05 + FR06).

Runs one fictional student through the whole chain without Streamlit:

    reviewed course data -> diagnostic scoring -> profile snapshot
    -> exact plan -> practice questions for the allocated topics

Exit code 0 means every check passed. Any failure prints FAIL lines and
exits non-zero.

Run from the repository root:
    python scripts/smoke.py
"""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.optimizer.classical import solve_exact  # noqa: E402

DATA = ROOT / "data" / "demo"
TOPICS = ("T1", "T2", "T3")
failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def load(name):
    with (DATA / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def topic_weights(course):
    count = course["assessment_count"]
    weights = {}
    for topic in course["topics"]:
        mentions = course["topic_counts"][topic["topic_id"]]
        weights[topic["topic_id"]] = 0.5 + 0.5 * (mentions / count)
    return weights


def score(answers, diagnostics):
    correct = {topic: 0 for topic in TOPICS}
    total = {topic: 0 for topic in TOPICS}
    for question_id, choice in answers.items():
        question = diagnostics[question_id]
        total[question["topic_id"]] += 1
        if choice == question["correct_choice"]:
            correct[question["topic_id"]] += 1
    return {topic: correct[topic] / total[topic] for topic in TOPICS}


def select_practice(course, allocations, proficiency):
    """Up to two approved practice items per allocated topic, never diagnostics."""
    picked = []
    for topic_id in TOPICS:
        if allocations[topic_id] <= 0:
            continue
        candidates = [
            q for q in course["questions"]
            if q["topic_id"] == topic_id
            and q["purpose"] == "practice"
            and q["review_status"] == "approved"
        ]
        target_difficulty = 1 if proficiency[topic_id] < 0.4 else (2 if proficiency[topic_id] < 0.7 else 3)
        candidates.sort(key=lambda q: (q["difficulty"] != target_difficulty, q["question_id"]))
        picked.extend(candidates[:2])
    return picked


def main():
    course = load("course.json")
    cases = load("student_cases.json")

    check(course["schema_version"] == 1, "course schema_version must be 1")
    check(len(course["questions"]) == 12, "course must hold 12 reviewed questions")

    diagnostics = {
        q["question_id"]: q for q in course["questions"] if q["purpose"] == "diagnostic"
    }
    practice = {
        q["question_id"]: q for q in course["questions"] if q["purpose"] == "practice"
    }
    check(len(diagnostics) == 6, "course must hold 6 diagnostic questions")
    check(len(practice) == 6, "course must hold 6 practice questions")
    check(not set(diagnostics) & set(practice), "diagnostic and practice ids must not overlap")

    weights = topic_weights(course)
    for topic in course["topics"]:
        suggested = weights[topic["topic_id"]]
        check(
            math.isclose(topic["importance"], suggested, abs_tol=1e-9),
            f"{topic['topic_id']} importance {topic['importance']} disagrees with topic_counts",
        )

    case = cases["cases"][0]
    check(set(case["submitted_choices"]) == set(diagnostics), "case-A must answer every diagnostic item")

    proficiency = score(case["submitted_choices"], diagnostics)
    expected = case["expected_with_test_weights"]["proficiency"]
    if cases["test_weights"]["topic_weights"] == {t: 1.0 for t in TOPICS}:
        check(proficiency == expected, f"scoring drifted: {proficiency} != {expected}")

    snapshot = {
        "schema_version": 1,
        "profile_source": "diagnostic",
        "request": {
            "budget_minutes": case["budget_minutes"],
            "proficiency": proficiency,
            "requested_solver": "exact",
        },
        "topic_weights": weights,
    }
    check(snapshot["request"]["budget_minutes"] == case["budget_minutes"], "snapshot kept the budget")

    plan = solve_exact(weights, snapshot["request"]["proficiency"], case["budget_minutes"])

    rebuilt = sum(
        weights[t] * (1 - proficiency[t]) * (1.0 + 0.5 * (plan["allocations"][t] == 60))
        for t in TOPICS
        if plan["allocations"][t] > 0
    )
    check(math.isclose(plan["utility"], rebuilt, abs_tol=1e-9), "reported utility differs from the model")

    check(plan["feasible"] is True, "plan must be feasible")
    check(plan["used_minutes"] <= case["budget_minutes"], "plan overspends the budget")
    check(all(m in (0, 30, 60) for m in plan["allocations"].values()), "allocations must be 0/30/60")

    picked = select_practice(course, plan["allocations"], proficiency)
    check(len(picked) >= 1, "at least one practice item is expected for this profile")
    for item in picked:
        check(item["purpose"] == "practice", f"{item['question_id']} is not a practice item")
        check(item["question_id"] in practice, f"{item['question_id']} is not in the practice pool")
        check(
            plan["allocations"][item["topic_id"]] > 0,
            f"{item['question_id']} belongs to unfunded topic {item['topic_id']}",
        )
        check(
            item["source_id"] and item["page"] >= 1,
            f"{item['question_id']} is missing a traceable source",
        )

    print(f"case            {case['case_id']} budget={case['budget_minutes']}")
    print(f"weights         {weights}")
    print(f"proficiency     {proficiency}")
    print(f"allocation      {plan['allocations']}  used={plan['used_minutes']}  utility={plan['utility']:.4f}")
    print(f"practice        {[q['question_id'] for q in picked]}")

    if failures:
        for message in failures:
            print(f"FAIL {message}")
        return 1

    print("SMOKE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
