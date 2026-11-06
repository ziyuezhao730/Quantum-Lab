"""risi checks for alex's scoring, validation & snapshot export"""
import copy
import json
from pathlib import Path

import pytest

from src.contracts import PlanRequest
from src.intelligence.assess import score_diagnostic
from src.intelligence.pipeline import load_course, make_snapshot
from src.intelligence.validate import validate_course, validate_snapshot
from src.intelligence import rank

DATA=Path(__file__).resolve().parents[1]/"data/demo"


@pytest.fixture
def course():
    return load_course(DATA/"course.json")


@pytest.mark.parametrize("correct,expected", [(True,1.0),(False,0.0)])
def test_all_correct_or_wrong(course,correct,expected):
    answers={}
    for q in course.questions:
        if q.purpose == "diagnostic":
            answers[q.question_id]=q.correct_choice if correct else next(c for c in q.choices if c != q.correct_choice)
    result=score_diagnostic(course,answers)
    assert result.proficiency == dict.fromkeys(("T1","T2","T3"),expected)
    assert result.submitted_choices == answers


@pytest.mark.parametrize("case_index", [0,1])
def test_reviewed_fictional_scores(course,case_index):
    case=json.loads((DATA/"student_cases.json").read_text())["cases"][case_index]
    result=score_diagnostic(course,case["submitted_choices"])
    assert result.proficiency == case["expected_with_test_weights"]["proficiency"]


@pytest.mark.parametrize("problem", ["missing","invalid","unexpected"])
def test_bad_answers_rejected(course,problem):
    answers={q.question_id:q.correct_choice for q in course.questions if q.purpose=="diagnostic"}
    key=next(iter(answers))
    if problem=="missing":
        answers.pop(key)
    elif problem=="invalid":
        answers[key]="not-a-choice"
    else:
        answers["not-a-question"]="A"
    with pytest.raises(ValueError):
        score_diagnostic(course,answers)


@pytest.mark.parametrize("problem", ["duplicate_id","wrong_role","missing_source","invalid_key","nan"])
def test_bad_course_rejected(problem):
    data=json.loads((DATA/"course.json").read_text())
    q=next(q for q in data["questions"] if q["purpose"]=="diagnostic")
    if problem=="duplicate_id":
        data["questions"].append(copy.deepcopy(q))
    elif problem=="wrong_role":
        q["purpose"]="practice"
    elif problem=="missing_source":
        q["source_id"]="missing"
    elif problem=="invalid_key":
        q["correct_choice"]="not-a-choice"
    else:
        data["topics"][0]["importance"]=float("nan")
    with pytest.raises(ValueError):
        validate_course(data)


def test_export_roundtrip_and_actual_weights(course):
    request=PlanRequest(budget_minutes=95,proficiency={"T1":1.0,"T2":0.0,"T3":0.5},requested_solver="exact")
    snapshot=make_snapshot(course,request)
    assert snapshot.request==request
    assert snapshot.topic_weights==pytest.approx({"T1":5/6,"T2":2/3,"T3":5/6})
    assert validate_snapshot(json.loads(snapshot.model_dump_json()))==snapshot


@pytest.mark.parametrize("topic,score", [(t,s) for t in ("T1","T2","T3") for s in (0.0,0.5)])
@pytest.mark.skipif(not callable(getattr(rank,"select_questions",None)), reason="blocked - production ranking & reviewed top-id oracle missing")
def test_retrieval_frozen_cases(course,topic,score):
    # require reviewed cases rather than invent expected top ids
    path=DATA/"retrieval_cases.json"
    assert path.read_text().strip(), "reviewed retrieval cases missing"
    cases=json.loads(path.read_text())["cases"]
    case=next(c for c in cases if c["topic_id"]==topic and c["proficiency"]==score)
    from src.contracts import PlanResult
    plan=PlanResult(allocations={t:30 if t==topic else 0 for t in ("T1","T2","T3")},used_minutes=30,unused_minutes=0,utility=0.0,feasible=True,actual_solver="exact",execution_mode="live",elapsed_ms=0.0)
    items=rank.select_questions(course,plan,dict.fromkeys(("T1","T2","T3"),score))
    assert items and items[0].question_id in case["acceptable_top_ids"]
    approved={q.question_id for q in course.questions if q.purpose=="practice" and q.topic_id==topic and q.review_status=="approved"}
    assert len(items)<=2
    assert len({i.question_id for i in items})==len(items)
    assert all(i.question_id in approved for i in items)
