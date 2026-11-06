import json
import warnings
from pathlib import Path

from src.contracts import CourseData, PlanRequest, ProfileSnapshot
from src.intelligence.validate import validate_course, validate_snapshot


def load_course(json_path: str | Path) -> CourseData:
    path = Path(json_path)

    with path.open("r", encoding="utf-8") as file:
        candidate = json.load(file)

    return validate_course(candidate)

def make_snapshot(
    course: CourseData,
    request: PlanRequest | dict,
) -> ProfileSnapshot:
    course = validate_course(course)

    if isinstance(request, PlanRequest):
        request_data = request.model_dump()
    else:
        request_data = request

    validated_request = PlanRequest.model_validate(request_data)

    if course.assessment_count == 0:
        warnings.warn(
            "No assessments available; using topic weights of 0.5.",
            UserWarning,
            stacklevel=2,
        )

    topic_weights = {}

    for topic in course.topics:
        if course.assessment_count == 0:
            weight = 0.5
        else:
            frequency = (
                course.topic_counts[topic.topic_id]
                / course.assessment_count
            )
            weight = 0.5 + 0.5 * frequency

        topic_weights[topic.topic_id] = weight

    return validate_snapshot(
        {
            "schema_version": 1,
            "profile_source": "diagnostic",
            "request": validated_request.model_dump(),
            "topic_weights": topic_weights,
        }
    )