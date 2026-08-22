"""Autonomous Loop (TASK-053).

A closed-loop control cycle for autonomous goals: OBSERVE → ASSESS → PLAN →
VALIDATE → ACT → OBSERVE → EVALUATE → LEARN → DECIDE. The loop *coordinates*
primitives from T050/T051/T052/M5/M6; it never directly executes tools or
runtime operations. All actions still flow through Policy, Permission,
Runtime and Evidence.
"""

from aios.autonomous_loop.contracts import (
    AutonomousCycle,
    CycleStatus,
    Decision,
    StopCondition,
)
from aios.autonomous_loop.loop import AutonomousLoop, LoopController

__all__ = [
    "AutonomousCycle",
    "CycleStatus",
    "Decision",
    "StopCondition",
    "AutonomousLoop",
    "LoopController",
]
