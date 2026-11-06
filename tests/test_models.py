import math

import pytest
from pydantic import ValidationError

from src.contracts import PlanRequest, PlanResult, QuantumMetrics


@pytest.fixture
def request_data():
    return dict(budget_minutes=90, proficiency=dict(T1=0.0, T2=0.5, T3=1.0),
                requested_solver="exact")


@pytest.fixture
def result_data():
    return dict(allocations=dict(T1=0, T2=30, T3=60), used_minutes=90,
                unused_minutes=0, utility=2.5, feasible=True, actual_solver="exact",
                execution_mode="live", elapsed_ms=1.25)


@pytest.fixture
def metrics_data():
    return dict(qubits=6, p=2, shots=1024, seed=0, feasible_shot_rate=0.75)


def reject(model, data, field, value):
    with pytest.raises(ValidationError) as exc:
        model(**(data | {field: value}))
    assert any(error["loc"][0] == field for error in exc.value.errors())


@pytest.mark.parametrize("budget", [0, 180])
def test_budget_endpoints(request_data, budget):
    assert PlanRequest(**(request_data | {"budget_minutes": budget})).budget_minutes == budget


@pytest.mark.parametrize("budget", [-1, 181, 1.5, True, False])
def test_invalid_budget(request_data, budget):
    reject(PlanRequest, request_data, "budget_minutes", budget)


@pytest.mark.parametrize("model,fixture,field,values", [
    (PlanRequest, "request_data", "proficiency", dict(T1=0.0, T2=0.5, T3=1.0)),
    (PlanResult, "result_data", "allocations", dict(T1=0, T2=30, T3=60)),
])
def test_exact_topic_keys(model, fixture, field, values, request):
    data = request.getfixturevalue(fixture)
    assert getattr(model(**(data | {field: values})), field) == values
    for invalid in ({}, {k: v for k, v in values.items() if k != "T3"},
                    values | {"T4": 0}, {"OTHER" if k == "T3" else k: v for k, v in values.items()}):
        reject(model, data, field, invalid)


@pytest.mark.parametrize("value", [-0.01, 1.01, math.nan, math.inf, -math.inf])
def test_invalid_proficiency(request_data, value):
    for topic in ("T1", "T2", "T3"):
        reject(PlanRequest, request_data, "proficiency", request_data["proficiency"] | {topic: value})


@pytest.mark.parametrize("model,fixture,field,allowed", [
    (PlanRequest, "request_data", "requested_solver", ("exact", "qaoa")),
    (PlanResult, "result_data", "actual_solver", ("exact", "qaoa")),
    (PlanResult, "result_data", "execution_mode", ("live", "cached_replay")),
])
def test_solver_and_execution_literals(model, fixture, field, allowed, request):
    data = request.getfixturevalue(fixture)
    for value in allowed:
        assert getattr(model(**(data | {field: value})), field) == value
    for value in ("unknown", "", allowed[0].upper(), None, 1):
        reject(model, data, field, value)


@pytest.mark.parametrize("value", [0, 30, 60])
def test_valid_allocation_values(result_data, value):
    allocations = dict.fromkeys(("T1", "T2", "T3"), value)
    assert PlanResult(**(result_data | {"allocations": allocations})).allocations == allocations


@pytest.mark.parametrize("value", [-1, 1, 45, 90, "30", None])
def test_invalid_allocation_values(result_data, value):
    reject(PlanResult, result_data, "allocations", result_data["allocations"] | {"T2": value})


@pytest.mark.parametrize("field", ["utility", "elapsed_ms"])
@pytest.mark.parametrize("value", [-0.01, math.nan, math.inf, -math.inf])
def test_invalid_utility_and_timing(result_data, field, value):
    reject(PlanResult, result_data, field, value)


@pytest.mark.parametrize("field,minimum", [("qubits", 1), ("p", 1), ("shots", 1), ("seed", 0)])
def test_metric_integer_bounds(metrics_data, field, minimum):
    assert getattr(QuantumMetrics(**(metrics_data | {field: minimum})), field) == minimum
    reject(QuantumMetrics, metrics_data, field, minimum - 1)


@pytest.mark.parametrize("rate", [0.0, 1.0])
def test_valid_feasible_shot_rate(metrics_data, rate):
    assert QuantumMetrics(**(metrics_data | {"feasible_shot_rate": rate})).feasible_shot_rate == rate


@pytest.mark.parametrize("rate", [-0.01, 1.01, math.nan, math.inf, -math.inf])
def test_invalid_feasible_shot_rate(metrics_data, rate):
    reject(QuantumMetrics, metrics_data, "feasible_shot_rate", rate)


def test_nullable_fields(metrics_data, result_data):
    assert QuantumMetrics(**metrics_data).raw_best_utility is None
    assert QuantumMetrics(**(metrics_data | {"raw_best_utility": None})).raw_best_utility is None
    assert QuantumMetrics(**(metrics_data | {"raw_best_utility": 0.0})).raw_best_utility == 0.0
    assert PlanResult(**result_data).quantum_metrics is None
    assert PlanResult(**(result_data | {"quantum_metrics": None})).quantum_metrics is None
    nested = PlanResult(**(result_data | {"quantum_metrics": metrics_data}))
    assert nested.quantum_metrics == QuantumMetrics(**metrics_data)
    reject(PlanResult, result_data, "quantum_metrics", "invalid")


@pytest.mark.parametrize("value", [-0.01, math.nan, math.inf, -math.inf])
def test_invalid_raw_best_utility(metrics_data, value):
    reject(QuantumMetrics, metrics_data, "raw_best_utility", value)


def test_serialization_preserves_values(request_data, result_data, metrics_data):
    metrics = QuantumMetrics(**(metrics_data | {"raw_best_utility": 2.5}))
    examples = [PlanRequest(**request_data), metrics, QuantumMetrics(**metrics_data),
                PlanResult(**result_data),
                PlanResult(**(result_data | {"actual_solver": "qaoa", "quantum_metrics": metrics,
                                            "warnings": ["limited shots"]}))]
    for original in examples:
        restored = type(original).model_validate_json(original.model_dump_json())
        assert restored == original
        assert restored.model_dump() == original.model_dump()
