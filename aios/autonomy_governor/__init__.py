"""Autonomy Governor (TASK-054).

Gates every autonomous action before execution: scope / risk / policy /
permission / resource-budget / action-limit / approval checks. The Governor
does NOT replace the Policy Engine — it is the autonomy-specific governance
layer that consumes existing policy/permission/runtime contracts. Fail-closed:
uncertainty → BLOCK.
"""

from aios.autonomy_governor.contracts import (
    ApprovalRequest,
    AutonomyAction,
    AutonomyBudget,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
    AutonomyRisk,
)
from aios.autonomy_governor.governor import AutonomyGovernor

__all__ = [
    "ApprovalRequest",
    "AutonomyAction",
    "AutonomyBudget",
    "AutonomyDecision",
    "AutonomyMode",
    "AutonomyPolicy",
    "AutonomyRisk",
    "AutonomyGovernor",
]
