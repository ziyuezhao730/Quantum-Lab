import copy
from pathlib import Path

from src.contracts import PlanRequest
from src.intelligence.pipeline import load_course,make_snapshot
from src.optimizer.classical import solve_plan
from src.intelligence.rank import select_questions


def test_dedup_pending_and_diagnostic_exclusion():
    course=load_course(Path(__file__).resolve().parents[1]/"data/demo/course.json")
    request=PlanRequest(budget_minutes=180,proficiency={"T1":0.,"T2":0.,"T3":0.},requested_solver="exact")
    snapshot=make_snapshot(course,request)
    plan=solve_plan(snapshot.topic_weights,request)
    first=next(q for q in course.questions if q.purpose=="practice")
    duplicate=first.model_copy(update={"question_id":"duplicate","text":"  "+first.text.upper()+"  "})
    pending=first.model_copy(update={"question_id":"pending","review_status":"pending"})
    changed=course.model_copy(update={"questions":course.questions+[duplicate,pending]})
    items=select_questions(changed,plan,request.proficiency)
    ids=[i.question_id for i in items]
    assert "pending" not in ids
    by_id={q.question_id:q for q in changed.questions}
    texts=[" ".join(by_id[i].text.casefold().split()) for i in ids]
    assert len(texts)==len(set(texts))
    assert all(by_id[i].purpose=="practice" for i in ids)


def test_no_allocations_or_empty_practice():
    course=load_course(Path(__file__).resolve().parents[1]/"data/demo/course.json")
    request=PlanRequest(budget_minutes=0,proficiency={"T1":0.,"T2":0.,"T3":0.},requested_solver="exact")
    plan=solve_plan({"T1":1.,"T2":1.,"T3":1.},request)
    assert select_questions(course,plan,request.proficiency)==[]
    plan=plan.model_copy(update={"allocations":{"T1":30,"T2":0,"T3":0}})
    assert select_questions(course.model_copy(update={"questions":[]}),plan,request.proficiency)==[]
