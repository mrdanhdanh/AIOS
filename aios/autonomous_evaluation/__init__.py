"""Autonomous Evaluation — Decision Layer (TASK-060).

The decision layer for the Autonomous Loop: after each step/cycle, evaluate
the outcome (via Harness T030/T032) and map the verdict to a *decision
candidate*. The Governor (T054) then decides whether the agent is *allowed*
to execute that decision. Evaluation ≠ Decision ≠ Governor.
"""

from aios.autonomous_evaluation.contracts import Decision, DecisionPolicy, EvaluationRecord
from aios.autonomous_evaluation.evaluator import (
    DecisionMapper,
    LoopGate,
    StepEvaluator,
)

__all__ = [
    "Decision",
    "DecisionPolicy",
    "EvaluationRecord",
    "DecisionMapper",
    "LoopGate",
    "StepEvaluator",
]
