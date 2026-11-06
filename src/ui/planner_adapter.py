"""compatibility helpers for the earlier ui branch"""
from pathlib import Path
from src.contracts import PlanRequest
from src.intelligence.pipeline import load_course,make_snapshot


def load_course_data():
    return load_course(Path(__file__).resolve().parents[2]/"data/demo/course.json").model_dump()


def get_topic_weights(course):
    request=PlanRequest(budget_minutes=0,proficiency={"T1":0.,"T2":0.,"T3":0.},requested_solver="exact")
    return make_snapshot(course,request).topic_weights


def get_topic_names(course):
    return {t["topic_id"]:t["name"] for t in course["topics"]}


def get_practice_questions(course):
    return [{"text":q["text"],"source":f"{q['source_id']}, page {q['page']}","answer":q["answer"]} for q in course["questions"] if q["purpose"]=="practice" and q["review_status"]=="approved"]
