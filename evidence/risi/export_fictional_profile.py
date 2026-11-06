"""export a fictional diagnostic through the production pipeline"""
import json
from pathlib import Path

from src.contracts import PlanRequest
from src.intelligence.assess import score_diagnostic
from src.intelligence.pipeline import load_course, make_snapshot


def main():
    root = Path(__file__).resolve().parents[2]
    data = root / "data/demo"
    case = json.loads((data / "student_cases.json").read_text())["cases"][0]
    course = load_course(data / "course.json")
    diagnostic = score_diagnostic(course, case["submitted_choices"])
    request = PlanRequest(
        budget_minutes=case["budget_minutes"],
        proficiency=diagnostic.proficiency,
        requested_solver="exact",
    )
    snapshot = make_snapshot(course, request)
    output = root / "runtime/student_profile.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(snapshot.model_dump_json(indent=2) + "\n")
    print(f"fictional profile - {output}")


if __name__ == "__main__":
    main()
