from math import isclose

import pytest

from src.contracts import PlanRequest
from src.optimizer.model import (
    binary_energy, build_binary_model, polynomial_energy, binary_to_ising,
    ising_energy, decode_bits, qiskit_bitstring_to_bits,
)

weights = dict.fromkeys(("T1", "T2", "T3"), 1.0)
scores = {"T1": 0.8, "T2": 0.2, "T3": 0.4}


def request(budget):
    return PlanRequest(budget_minutes=budget, proficiency=scores, requested_solver="qaoa")


# expected vals from hand calc, p=3.4
@pytest.mark.parametrize("budget,bits,expected,feasible", [
    (0, [0]*9, 0.0, True),
    (90, [0,0,0,0,0,0,1,1,0], 0.0, True),
    (180, [0,0,0,0,0,0,0,1,1], 0.0, True),
    (90, [0,0,1,1,1,0,0,0,0], -1.8, True),
    (180, [1,1,1,1,1,1,0,0,0], -2.4, True),
    (90, [0,1,1,0,1,0,0,0,0], 1.9, False),
    (0, [0,1,0,0,0,0,0,0,0], 6.7, False),
    (180, [0,1,0,0,0,0,1,0,1], 3.3, False),
    (90, [0]*9, 30.6, False),
    (0, [1,0,0,0,0,0,0,0,0], 3.2, False),
])
def test_known_energies_and_decoding(budget, bits, expected, feasible):
    profile = request(budget)
    binary = build_binary_model(weights, profile)
    ising = binary_to_ising(binary)
    for energy in (binary_energy(bits, weights, profile),
                   polynomial_energy(bits, binary), ising_energy(bits, ising)):
        assert isclose(energy, expected, rel_tol=0, abs_tol=1e-8)
    assert decode_bits(bits, weights, profile)["feasible"] is feasible


def test_decode_reference_and_partial_budget():
    bits = [0,0,1,1,1,0,0,0,0]
    decoded = decode_bits(bits, weights, request(95))
    assert decoded["allocations"] == {"T1": 0, "T2": 60, "T3": 30}
    assert decoded["used_minutes"] == 90
    assert decoded["unused_minutes"] == 5
    assert decoded["feasible"]
    assert isclose(decoded["utility"], 1.8)


def test_qiskit_display_order():
    assert qiskit_bitstring_to_bits("000011100") == [0,0,1,1,1,0,0,0,0]
    assert qiskit_bitstring_to_bits("100000000") == [0,0,0,0,0,0,0,0,1]


@pytest.mark.parametrize("bits", [[0]*8, [0]*10, [0]*8+[2], [False]+[0]*8, [0.0]*9])
def test_rejects_malformed_bits(bits):
    with pytest.raises(ValueError):
        binary_energy(bits, weights, request(90))
    with pytest.raises(ValueError):
        decode_bits(bits, weights, request(90))


def test_zero_utility_and_nonunit_weights():
    profile = PlanRequest(budget_minutes=90, proficiency={"T1": 1.0, "T2": 1.0, "T3": 1.0}, requested_solver="qaoa")
    weights = {"T1": 0.5, "T2": 0.75, "T3": 1.0}
    bits = [0,0,0,0,0,0,1,1,0]
    binary = build_binary_model(weights, profile)
    assert binary_energy(bits, weights, profile) == 0
    assert isclose(ising_energy(bits, binary_to_ising(binary)), 0, abs_tol=1e-8)


def test_nonunit_weights_energy():
    weights = {"T1": 0.5, "T2": 0.75, "T3": 1.0}
    bits = [0,0,1,1,1,0,0,0,0]
    # vals .1, .6, .6; util = 1.5
    binary = build_binary_model(weights, request(90))
    assert isclose(binary_energy(bits, weights, request(90)), -1.5)
    assert isclose(polynomial_energy(bits, binary), -1.5, abs_tol=1e-8)
    assert isclose(ising_energy(bits, binary_to_ising(binary)), -1.5, abs_tol=1e-8)
