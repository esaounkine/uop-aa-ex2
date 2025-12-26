from enum import Enum

"""
States of the orchestrator agent
"""

class State(Enum):
    INIT = 0
    FAILURE_DETECTION = 1
    IMPACT_ANALYSIS = 2
    REPAIR_PLANNING = 3
    EXECUTION = 4
    RESCHEDULING = 5
    FINAL = 6
