import json
from pathlib import Path


def test_question_counts():
    course_path = (
        Path(__file__).resolve().parents[1]
        / "data" / "demo" / "course.json"
    )

    with course_path.open("r", encoding="utf-8") as file:
        course = json.load(file)

    questions = course["questions"]

    assert len(questions) == 12

    for topic_id in ["T1", "T2", "T3"]:
        diagnostic = [
            q for q in questions
            if q["topic_id"] == topic_id
            and q["purpose"] == "diagnostic"
        ]

        practice = [
            q for q in questions
            if q["topic_id"] == topic_id
            and q["purpose"] == "practice"
        ]

        assert len(diagnostic) == 2
        assert len(practice) == 2

def test_question_ids_and_answers():
    course_path = (
        Path(__file__).resolve().parents[1]
        / "data" / "demo" / "course.json"
    )

    with course_path.open("r", encoding="utf-8") as file:
        course = json.load(file)

    questions = course["questions"]

    # Check 1: Every question ID must be unique
    question_ids = [q["question_id"] for q in questions]

    assert len(question_ids) == len(set(question_ids))

    # Check 2: Validate answers
    for question in questions:
        if question["purpose"] == "diagnostic":
            choices = question["choices"]
            correct = question["correct_choice"]

            assert set(choices.keys()) == {"A", "B", "C", "D"}
            assert correct in choices

        elif question["purpose"] == "practice":
            assert isinstance(question["answer"], str)
            assert question["answer"].strip()

def test_question_sources_and_review_status():
    course_path = (
        Path(__file__).resolve().parents[1]
        / "data" / "demo" / "course.json"
    )

    with course_path.open("r", encoding="utf-8") as file:
        course = json.load(file)

    for question in course["questions"]:

        # Every question must have a source
        assert isinstance(question["source_id"], str)
        assert question["source_id"].strip()

        # Every question must have a valid page number
        assert isinstance(question["page"], int)
        assert not isinstance(question["page"], bool)
        assert question["page"] >= 1

        # Every demo question must be approved
        assert question["review_status"] == "approved"

def test_student_cases():
    base_path = Path(__file__).resolve().parents[1] / "data" / "demo"

    with (base_path / "course.json").open("r", encoding="utf-8") as file:
        course = json.load(file)

    with (base_path / "student_cases.json").open("r", encoding="utf-8") as file:
        students = json.load(file)

    diagnostic_questions = {
        q["question_id"]: q
        for q in course["questions"]
        if q["purpose"] == "diagnostic"
    }

    cases = students["cases"]

    # There must be two distinct fictional students
    assert len(cases) == 2
    assert len({case["case_id"] for case in cases}) == 2

    for case in cases:
        choices = case["submitted_choices"]
        expected = case["expected_with_test_weights"]

        # Every diagnostic question must be answered
        assert set(choices) == set(diagnostic_questions)

        # Every submitted answer must be valid
        for question_id, answer in choices.items():
            assert answer in diagnostic_questions[question_id]["choices"]

        # Expected proficiency must match actual answers
        for topic_id in ["T1", "T2", "T3"]:
            topic_questions = [
                q for q in diagnostic_questions.values()
                if q["topic_id"] == topic_id
            ]

            correct_count = sum(
                choices[q["question_id"]] == q["correct_choice"]
                for q in topic_questions
            )

            actual_proficiency = correct_count / len(topic_questions)

            assert actual_proficiency == expected["proficiency"][topic_id]

        # Expected allocation must respect the budget
        allocations = expected["exact_allocation"]

        assert set(allocations) == {"T1", "T2", "T3"}
        assert all(minutes in (0, 30, 60) for minutes in allocations.values())

        assert sum(allocations.values()) == expected["used_minutes"]

        assert (
            expected["used_minutes"] + expected["unused_minutes"]
            == case["budget_minutes"]
        )  