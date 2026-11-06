from src.contracts import CourseData, ProfileSnapshot


def validate_course(candidate: dict | CourseData) -> CourseData:
    if isinstance(candidate, CourseData):
        candidate = candidate.model_dump()

    course = CourseData.model_validate(candidate)

    expected_topics = {"T1", "T2", "T3"}
    topic_ids = set()

    for topic in course.topics:
        if topic.topic_id in topic_ids:
            raise ValueError(f"Duplicate topic ID: {topic.topic_id}")

        topic_ids.add(topic.topic_id)

    if topic_ids != expected_topics:
        raise ValueError("Course must contain exactly T1, T2, and T3")

    source_ids = set()

    for source in course.sources:
        if source.source_id in source_ids:
            raise ValueError(f"Duplicate source ID: {source.source_id}")

        source_ids.add(source.source_id)

        label = (source.label or "").strip()
        filename = (source.filename or "").strip()

        if not label and not filename:
            raise ValueError(
                f"Source {source.source_id} needs a label or filename"
            )

    if set(course.topic_counts) != expected_topics:
        raise ValueError(
            "topic_counts must contain exactly T1, T2, and T3"
        )

    for topic in course.topics:
        count = course.topic_counts[topic.topic_id]

        if count > course.assessment_count:
            raise ValueError(
                f"Topic count exceeds assessment_count: {topic.topic_id}"
            )

        for evidence in topic.evidence:
            if evidence.source_id not in source_ids:
                raise ValueError(
                    f"Unknown evidence source: {evidence.source_id}"
                )

    question_ids = set()
    role_counts = {}

    for topic in course.topics:
        role_counts[topic.topic_id] = {
            "diagnostic": 0,
            "practice": 0,
        }

    for question in course.questions:
        if question.question_id in question_ids:
            raise ValueError(
                f"Duplicate question ID: {question.question_id}"
            )

        question_ids.add(question.question_id)

        if question.source_id not in source_ids:
            raise ValueError(
                f"Unknown source for question {question.question_id}: "
                f"{question.source_id}"
            )

        if question.review_status != "approved":
            raise ValueError(
                f"Question is not approved: {question.question_id}"
            )

        role_counts[question.topic_id][question.purpose] += 1

        if question.purpose == "diagnostic":
            choices = question.choices

            if choices is None or len(choices) < 2:
                raise ValueError(
                    f"Diagnostic needs at least two choices: "
                    f"{question.question_id}"
                )

            for choice_id, text in choices.items():
                if not choice_id.strip() or not text.strip():
                    raise ValueError(
                        f"Diagnostic has an empty choice: "
                        f"{question.question_id}"
                    )

            if len(set(choices.values())) != len(choices):
                raise ValueError(
                    f"Diagnostic has duplicate choice text: "
                    f"{question.question_id}"
                )

            if question.correct_choice not in choices:
                raise ValueError(
                    f"Diagnostic has an invalid correct_choice: "
                    f"{question.question_id}"
                )

    for topic_id, counts in role_counts.items():
        if counts["diagnostic"] != 2 or counts["practice"] != 2:
            raise ValueError(
                f"{topic_id} must have exactly two diagnostic "
                f"and two practice questions"
            )

    return course

def validate_snapshot(
    candidate: dict | ProfileSnapshot,
) -> ProfileSnapshot:
    if isinstance(candidate, ProfileSnapshot):
        candidate = candidate.model_dump()

    return ProfileSnapshot.model_validate(candidate)