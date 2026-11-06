import json
from pathlib import Path

from src.contracts import CourseData
from src.intelligence.validate import validate_course


def load_course(json_path: str | Path) -> CourseData:
    path = Path(json_path)

    with path.open("r", encoding="utf-8") as file:
        candidate = json.load(file)

    return validate_course(candidate)