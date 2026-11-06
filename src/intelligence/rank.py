from numbers import Real

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.contracts import CourseData, PlanResult, PracticeItem


def select_questions(
    course: CourseData,
    plan: PlanResult,
    proficiency: dict[str, float],
) -> list[PracticeItem]:
    """Return ranked practice questions for allocated topics."""
    topics = {}

    for topic in course.topics:
        topics[topic.topic_id] = topic

    if set(plan.allocations) != set(topics):
        raise ValueError("Plan topic IDs must match course topic IDs")

    if set(proficiency) != set(topics):
        raise ValueError("Proficiency topic IDs must match course topic IDs")

    if not plan.feasible:
        raise ValueError("Cannot select practice for an infeasible plan")

    for topic_id in topics:
        value = proficiency[topic_id]

        if (
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not 0 <= value <= 1
        ):
            raise ValueError(f"Invalid proficiency for {topic_id}")

        minutes = plan.allocations[topic_id]

        if (
            isinstance(minutes, bool)
            or not isinstance(minutes, int)
            or minutes < 0
        ):
            raise ValueError(f"Invalid allocated minutes for {topic_id}")

    topic_ids = sorted(
        topics,
        key=lambda topic_id: (
            -plan.allocations[topic_id],
            topic_id,
        ),
    )

    questions_by_id = {}

    for question in course.questions:
        questions_by_id[question.question_id] = question

    selected = []
    seen_text = set()

    for topic_id in topic_ids:
        if plan.allocations[topic_id] == 0:
            continue

        topic = topics[topic_id]
        level = proficiency[topic_id]

        if level < 0.4:
            target_difficulty = 1
        elif level < 0.7:
            target_difficulty = 2
        else:
            target_difficulty = 3

        candidates = []

        for question in course.questions:
            if (
                question.topic_id == topic_id
                and question.purpose == "practice"
                and question.review_status == "approved"
                and question.text.strip()
            ):
                candidates.append(question)

        if not candidates:
            continue

        query_parts = [topic.name]

        for evidence in topic.evidence:
            query_parts.append(evidence.excerpt)

        query = " ".join(query_parts)

        documents = []

        for question in candidates:
            documents.append(question.text)

        documents.append(query)

        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            lowercase=False,
        )

        vectors = vectorizer.fit_transform(documents)

        similarities = cosine_similarity(
            vectors[-1],
            vectors[:-1],
        )[0]

        ranked = []

        for question, similarity in zip(candidates, similarities):
            similarity = max(0.0, min(1.0, float(similarity)))

            difficulty_match = (
                1.0 if question.difficulty == target_difficulty else 0.0
            )

            score = (
                0.7 * similarity
                + 0.3 * difficulty_match
            )

            ranked.append(
                PracticeItem(
                    question_id=question.question_id,
                    score=score,
                    reason=(
                        f"Topic {topic_id}; "
                        f"text similarity {similarity:.3f}; "
                        f"difficulty {question.difficulty}, "
                        f"target {target_difficulty}."
                    ),
                )
            )

        ranked.sort(
            key=lambda item: (-item.score, item.question_id)
        )

        chosen_for_topic = 0

        for item in ranked:
            question = questions_by_id[item.question_id]
            normalized_text = " ".join(question.text.split())

            if normalized_text in seen_text:
                continue

            selected.append(item)
            seen_text.add(normalized_text)
            chosen_for_topic += 1

            if chosen_for_topic == 2:
                break

    return selected