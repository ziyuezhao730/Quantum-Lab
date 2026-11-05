
import json
from pathlib import Path


def load_course_data():
    """Load the approved demo course data."""
    course_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "demo"
        / "course.json"
    )

    with course_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_topic_weights(course):
    """Convert course topics into optimizer weights."""
    return {
        topic["topic_id"]: topic["importance"]
        for topic in course["topics"]
    }


def get_topic_names(course):
    """Map topic IDs to readable names."""
    return {
        topic["topic_id"]: topic["name"]
        for topic in course["topics"]
    }
