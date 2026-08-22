"""Autonomy Safety 1.0 (TASK-067) — bounded autonomy.

Bounded autonomy for goals/loops: per-context autonomy level, Governor (T054)
enforced boundary, and a fail-closed SAFE_STOP policy. This package is a
*safety layer* on top of the Autonomy Governor — it does NOT re-implement a
parallel autonomy controller.
"""

from __future__ import annotations

from aios.autonomy_safety.contracts import (
    AutonomyBudget,
    AutonomyContext,
    AutonomyLevel,
    RiskClass,
    SafeStopSignal,
    SafetyDecision,
)
from aios.autonomy_safety.registry import (
    AutonomyLevelRegistry,
    LevelPolicy,
)
from aios.autonomy_safety.boundary import (
    BoundaryResult,
    EvaluationResult,
    check_boundary,
    evaluate_action,
)
from aios.autonomy_safety.safe_stop import SafeStopPolicy

__all__ = [
    "AutonomyBudget",
    "AutonomyContext",
    "AutonomyLevel",
    "RiskClass",
    "SafeStopSignal",
    "SafetyDecision",
    "AutonomyLevelRegistry",
    "LevelPolicy",
    "BoundaryResult",
    "EvaluationResult",
    "check_boundary",
    "evaluate_action",
    "SafeStopPolicy",
]
