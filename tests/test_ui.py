"""integration checks against the actual streamlit entry point"""
import json
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from src.intelligence.validate import validate_snapshot

ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/"data/demo/student_cases.json").read_text())["cases"]


def submit(case_index=0,budget=90):
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=20).run()
    case=CASES[case_index]
    for qid,choice in case["submitted_choices"].items():
        app.radio(key=f"question_{qid}").set_value(choice)
    app.number_input(key="budget").set_value(budget)
    app.run()
    app.button(key="generate").click().run()
    assert not app.exception
    return app


def test_unanswered_start():
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=20).run()
    assert not app.exception
    assert len(app.radio)==6
    assert all(r.value is None for r in app.radio)
    assert app.button(key="generate").disabled
    assert len(app.get("download_button"))==0


def test_personalized_plan_and_snapshot():
    app=submit()
    saved=app.session_state["plan"]
    snapshot=validate_snapshot(json.loads(saved["snapshot"].model_dump_json()))
    assert snapshot.request.proficiency=={"T1":1.0,"T2":0.0,"T3":0.5}
    assert snapshot.request.budget_minutes==90
    assert saved["result"].allocations=={"T1":0,"T2":60,"T3":30}
    assert {item.question_id for item in saved["items"]}=={"Q-T2-P3","Q-T2-P4","Q-T3-P5","Q-T3-P6"}
    assert len(app.get("download_button"))==1
    assert 'test mode' not in str([c.value for c in app.caption]).lower()
    other=submit(1)
    assert other.session_state["plan"]["result"].allocations=={"T1":60,"T2":0,"T3":30}


def test_budget_clears_output_and_download():
    app=submit()
    app.number_input(key="budget").set_value(45).run()
    assert "plan" not in app.session_state
    assert len(app.get("download_button"))==0
    assert not app.exception


def test_answer_clears_output_and_download():
    app=submit()
    app.radio[0].set_value("C").run()
    assert "plan" not in app.session_state
    assert len(app.get("download_button"))==0


def test_zero_budget():
    app=submit(budget=0)
    assert app.session_state["plan"]["result"].used_minutes==0
    assert app.session_state["plan"]["items"]==[]
    assert any("no study blocks" in info.value for info in app.info)


def test_bad_course_error():
    with patch("src.intelligence.pipeline.load_course",side_effect=ValueError("bad fixture")):
        app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=20).run()
    assert not app.exception
    assert any("course data" in e.value for e in app.error)


def test_shortage_message():
    with patch("src.intelligence.rank.select_questions",return_value=[]):
        app=submit()
    assert len(app.warning)==2
    assert not app.exception
