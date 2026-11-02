"""Calculations used by study planner"""
import math
from numbers import Real

TOPICS = ("T1", "T2", "T3")

def priority(weight, proficiency):
    # dummy model
    return weight*(1-proficiency)

def value(priority, minutes):
    if minutes == 0:
        return 0.0
    if minutes == 30:
        return priority
    if minutes == 60:
        # diminishing returns
        return priority+priority*0.5