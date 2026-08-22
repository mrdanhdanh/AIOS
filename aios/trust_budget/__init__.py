"""Trust Budget + Autonomy Levels + SAFE-STOP (TASK-102, M15).

Trust accounting + safe-stop: each goal/loop carries a trust budget; risky
actions consume more trust; an empty budget triggers a fail-closed SAFE-STOP
(T068) and an action exceeding the remaining budget is BLOCKed (T054/T067).
"""

from aios.trust_budget.budget import (
    TrustBudget,
    TrustBudgetEngine,
    TrustScope,
)

__all__ = [
    "TrustBudget",
    "TrustBudgetEngine",
    "TrustScope",
]
