"""Long-Horizon Goal Durability & Durable Resume (TASK-056).

A goal-level durability layer on top of the existing Runtime (StateStore /
Executor / ExecutionGraph / AutonomousGoalEngine). It is NOT a new checkpoint
service or parallel subsystem. Checkpoints store authoritative execution
state + references (not memory payloads).
"""

from aios.goal_durability.contracts import (
    DurableCheckpoint,
    InterruptionCause,
    ResumeVerdict,
)
from aios.goal_durability.layer import GoalDurabilityLayer

__all__ = [
    "DurableCheckpoint",
    "InterruptionCause",
    "ResumeVerdict",
    "GoalDurabilityLayer",
]
