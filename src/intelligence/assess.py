from src.contracts import CourseData, DiagnosticResult
from src.intelligence.validate import validate_course


def score_diagnostic(
    course: CourseData,
    submitted_choices: dict[str, str],
) -> DiagnosticResult:
    course = validate_course(course)

    if not isinstance(submitted_choices, dict):
        raise ValueError("submitted_choices must be a dictionary")

    diagnostic_questions = {}

    for question in course.questions:
        if question.purpose == "diagnostic":
            diagnostic_questions[question.question_id] = question

    expected_ids = set(diagnostic_questions)
    submitted_ids = set(submitted_choices)

    missing_ids = expected_ids - submitted_ids
    unexpected_ids = submitted_ids - expected_ids

    if missing_ids:
        raise ValueError(
            f"Missing diagnostic answers: {sorted(missing_ids)}"
        )

    if unexpected_ids:
        raise ValueError(
            "Submission contains unexpected question IDs"
        )

    correct_counts = {}

    for topic in course.topics:
        correct_counts[topic.topic_id] = 0

    for question_id, question in diagnostic_questions.items():
        chosen = submitted_choices[question_id]
        choices = question.choices

        if (
            not isinstance(chosen, str)
            or choices is None
            or chosen not in choices
        ):
            raise ValueError(
                f"Invalid choice ID for question {question_id}"
            )

        if chosen == question.correct_choice:
            correct_counts[question.topic_id] += 1

    proficiency = {}

    for topic_id, correct_count in correct_counts.items():
        proficiency[topic_id] = correct_count / 2

    return DiagnosticResult(
        submitted_choices=submitted_choices.copy(),
        proficiency=proficiency,
    )