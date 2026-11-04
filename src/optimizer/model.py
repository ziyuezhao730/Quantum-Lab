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