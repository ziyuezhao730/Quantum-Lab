"""generates every possible plan"""
from itertools import product

from src.optimizer.model import plan_utility

product((0, 30, 60), repeat=3)

def solve_exact(weights, proficiency, budget):
    """find, by brute force, the highest utility allocation within budget given"""
    topic_ids = ("T1", "T2", "T3")

    # validation
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise ValueError("budget must be an integer number in minutes")
    if not 0 <= budget <= 180:
        raise ValueError("budget must be between 0 and 180")
    if set(weights) != set(topic_ids):
        raise ValueError("Weights must contain exactly T1, T2, T3")
    if set(proficiency) != set(topic_ids):
            raise ValueError("Proficiency must contain exactly T1, T2, T3")
    

    # set up
    best_allocs = None
    best_util = float("-inf")
    best_tie = None

    for mins in product((0, 30, 60), repeat=3):
        used_mins = sum(mins)
        # skip if overspent
        if used_mins > budget:
            continue

        allocs = dict(zip(topic_ids, mins))
        util = plan_utility(allocs, weights, proficiency)
        tie = (-used_mins, *mins)
        # accounting for floating point issues, values are subject to change
        better_util = util > best_util + 1e-12
        equal_util = abs(util-best_util) <= 1e-12

        if best_allocs is None or better_util or (equal_util and tie > best_tie):
            best_allocs = allocs
            best_util = util
            best_tie = tie

    used_mins = sum(best_allocs.values())

    return {
        "allocations": best_allocs,
        "used_minutes": used_mins,
        "unused_minutes": budget - used_mins,
        "utility": best_util,
    }
