"""calculations used by study planner"""
import math
from numbers import Real

TOPICS = ("T1", "T2", "T3")

def validate(val, name, min, max):
    """return a number within allowed range"""
    if isinstance(val, bool) or not isinstance(val, Real):
        raise ValueError(f"{name} must be a number")
    num = float(val)
    if not math.isfinite(num):
        raise ValueError(f"{name} must be finite")
    if not min <= num <= max:
        raise ValueError(
            f"{name} must not exceed min and max"
        )
    return num


def topic_priority(weight, proficiency):
    # dummy model
    weight = validate(weight, "Topic weight", 0.5, 1.0)
    proficiency = validate(proficiency, "Proficiency", 0.0, 1.0)
    return weight*(1-proficiency)

def plan_utility(allocations, topic_weights, proficiency):
    """calculates total utility(value) of a proposed study plan"""
    total = 0.0

    for topic_id, minutes in allocations.items():
        priority = topic_priority(
            topic_weights[topic_id],
            proficiency[topic_id],
        )

        total += topic_utility(priority, minutes)

    return total

def topic_utility(priority, minutes):
    if minutes == 0:
        return 0.0
    if minutes == 30:
        return priority
    if minutes == 60:
        # diminishing returns
        return priority+priority*0.5
    raise ValueError("minutes must be 0, 30, or 60")


def is_feasible(allocations, budget):
    """feasibility change for extra protection/ plan obeys given constraints"""
    if isinstance(budget, bool) or not isinstance(budget, int):
        return False
    if not 0 <= budget <= 180:
        return False
    if set(allocations) != set(TOPICS):
        return False

    for mins in allocations.values():
        if isinstance(mins, bool) or not isinstance(mins, int):
                return False
        if mins not in (0, 30, 60):
            return False

    return sum(allocations.values()) <= budget

# bit order fixed, slack bits start with lowest value
BIT_ORDER = ("x11", "x12", "x21", "x22", "x31", "x32", "y0", "y1", "y2")


def _check_bits(bits):
    if len(bits) != 9 or any(type(bit) is not int or bit not in (0, 1) for bit in bits):
        raise ValueError("expected 9 integer bits in bit_order")


def _profile_priorities(weights, request):
    if set(weights) != set(TOPICS):
        raise ValueError("weights must contain exactly T1, T2, T3")
    return [topic_priority(weights[t], request.proficiency[t]) for t in TOPICS]


def binary_energy(bits, weights, request):
    """calc energy directly from the given formula"""
    _check_bits(bits)
    vals = _profile_priorities(weights, request)
    penalty = 1 + 1.5 * sum(vals)
    blocks = request.budget_minutes // 30
    util = 0.0
    bad_order = 0
    for i, val in enumerate(vals):
        first, second = bits[2 * i:2 * i + 2]
        util += val * first + 0.5 * val * second
        bad_order += second * (1 - first)
    slack = bits[6] + 2 * bits[7] + 4 * bits[8]
    budget_diff = sum(bits[:6]) + slack - blocks
    return -util + penalty * (budget_diff ** 2 + bad_order)


def build_binary_model(weights, request):
    """build constant, linear and pair coeffs"""
    vals = _profile_priorities(weights, request)
    penalty = 1 + 1.5 * sum(vals)
    blocks = request.budget_minutes // 30
    counts = (1, 1, 1, 1, 1, 1, 1, 2, 4)
    values = [value for a in vals for value in (a, 0.5 * a)] + [0.0] * 3
    linear = []
    for j in range(9):
        coeff = penalty * counts[j] ** 2 - 2 * penalty * blocks * counts[j] - values[j]
        if j in (1, 3, 5):
            coeff += penalty
        linear.append(coeff)
    quadratic = {}
    for j in range(9):
        for k in range(j + 1, 9):
            coeff = 2 * penalty * counts[j] * counts[k]
            if (j, k) in ((0, 1), (2, 3), (4, 5)):
                coeff -= penalty
            quadratic[j, k] = coeff
    return {
        "constant": penalty * blocks ** 2,
        "linear": linear,
        "quadratic": quadratic,
    }


def polynomial_energy(bits, model):
    """calc binary energy, constant included"""
    _check_bits(bits)
    return (
        model["constant"]
        + sum(coeff * bits[j] for j, coeff in enumerate(model["linear"]))
        + sum(coeff * bits[j] * bits[k] for (j, k), coeff in model["quadratic"].items())
    )


def binary_to_ising(model):
    """convert binary to ising, keep offset"""
    linear = [-coeff / 2 for coeff in model["linear"]]
    offset = model["constant"] + sum(model["linear"]) / 2
    quadratic = {}
    for (j, k), coeff in model["quadratic"].items():
        coupling = coeff / 4
        quadratic[j, k] = coupling
        linear[j] -= coupling
        linear[k] -= coupling
        offset += coupling
    return {"offset": offset, "linear": linear, "quadratic": quadratic}


def ising_energy(bits, model):
    """calc ising energy, 0 maps to +1 and 1 maps to -1"""
    _check_bits(bits)
    spins = [1 - 2 * bit for bit in bits]
    return (
        model["offset"]
        + sum(coeff * spins[j] for j, coeff in enumerate(model["linear"]))
        + sum(coeff * spins[j] * spins[k] for (j, k), coeff in model["quadratic"].items())
    )


def decode_bits(bits, weights, request):
    """decode bits and check constraints"""
    _check_bits(bits)
    vals = _profile_priorities(weights, request)
    allocs = {}
    util = 0.0
    warnings = []
    for i, topic in enumerate(TOPICS):
        first, second = bits[2 * i:2 * i + 2]
        allocs[topic] = 30 * (first + second)
        util += vals[i] * (first + 0.5 * second)
        if second > first:
            warnings.append(f"{topic}: second block needs first block")
    slack = bits[6] + 2 * bits[7] + 4 * bits[8]
    if sum(bits[:6]) + slack != request.budget_minutes // 30:
        warnings.append("selected blocks + slack must equal budget blocks")
    if not is_feasible(allocs, request.budget_minutes):
        warnings.append("allocs exceed time constraints")
    used = sum(allocs.values())
    return {
        "allocations": allocs,
        "used_minutes": used,
        "unused_minutes": request.budget_minutes - used,
        "utility": util,
        "feasible": not warnings,
        "slack_blocks": slack,
        "warnings": warnings,
    }


def qiskit_bitstring_to_bits(bitstr):
    """reverse displayed bits into qubit order"""
    if not isinstance(bitstr, str) or len(bitstr) != 9 or set(bitstr) - {"0", "1"}:
        raise ValueError("expected 9 binary characters")
    return [int(bit) for bit in reversed(bitstr)]
