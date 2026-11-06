import copy
import json
from pathlib import Path

import pytest

from evidence.risi.replay_comparison import audit_report


def report():
    return json.loads(Path(__file__).with_name("r4_comparison.json").read_text())


def test_clean_committed_run():
    saved=report()
    snapshot=audit_report(saved)
    assert snapshot.model_dump(mode="json") == json.loads(Path(__file__).with_name("fictional_profile.json").read_text())
    assert saved["quantum"]["best_sample"]["feasible"]


@pytest.mark.parametrize("field,val", [("qubits",8),("shots",100),("seed",9),("feasible_shot_rate",1.0),("raw_best_utility",99.0)])
def test_changed_result_rejected(field,val):
    saved=copy.deepcopy(report())
    saved["quantum"][field]=val
    with pytest.raises(ValueError):
        audit_report(saved)


def test_changed_profile_rejected():
    saved=report()
    saved["profile"]["request"]["proficiency"]["T2"]=1.0
    with pytest.raises(ValueError):
        audit_report(saved)
