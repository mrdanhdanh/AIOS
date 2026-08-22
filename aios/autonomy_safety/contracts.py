"""Autonomy Safety contracts (TASK-067).

Data types for bounded autonomy: the autonomy context attached to a goal/loop,
the autonomy level enum, and the fail-closed SAFE_STOP signal type.

The Kill Switch (T068) is not yet available, so TASK-067 defines the canonical
``SafeStopSignal`` type here. When T068 lands, its emergency-stop hook can
consume this same signal (see ``aios/autonomy_safety/safe_stop.py``).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AutonomyLevel(str, Enum):
    """Bounded autonomy levels (spec §1).

    L0  fully human-in-loop
    L1  propose, human approve
    L2  execute bounded, escalate on risk
    L3  autonomous within policy
    L4  fully autonomous (restricted surfaces)
    """

    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"

    @property
    def rank(self) -> int:
        return int(self.value[1:])


class RiskClass(str, Enum):
    """Risk classes that may be listed in ``AutonomyContext.escalate_on``.

    Mirrors the Governor's ``AutonomyRisk`` (low/medium/high/critical) and the
    Recovery ``FailureClass`` vocabulary so escalation can be expressed uniformly.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    POLICY = "policy"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    STATE = "state"
    LOGICAL = "logical"
    TRANSIENT = "transient"
    UNKNOWN = "unknown"


class SafetyDecision(str, Enum):
    """Outcome of an autonomy safety evaluation."""

    ALLOW = "allow"
    BLOCK = "block"
    SAFE_STOP = "safe_stop"
    ESCALATE = "escalate"


@dataclass
class AutonomyBudget:
    """Cost/resource budget attached to an autonomy context (spec §2)."""

    max_cost: float = 1.0
    max_resource: float = 1.0
    max_steps: int = 20
    consumed_cost: float = 0.0
    consumed_resource: float = 0.0
    consumed_steps: int = 0

    def within(self) -> bool:
        return (
            self.consumed_cost <= self.max_cost
            and self.consumed_resource <= self.max_resource
            and self.consumed_steps <= self.max_steps
        )


@dataclass
class AutonomyContext:
    """Bounded autonomy context for a goal/loop (spec §2).

    Attributes
    ----------
    level:
        Autonomy level L0..L4 for this goal/loop.
    allowed_surfaces:
        The action surfaces (capabilities) permitted within the boundary.
    budget:
        Cost/resource budget for the goal/loop.
    escalate_on:
        Risk classes that must be escalated (not silently executed).
    evidence_ref:
        Provenance reference for the context assignment.
    """

    level: AutonomyLevel = AutonomyLevel.L0
    allowed_surfaces: list[str] = field(default_factory=list)
    budget: AutonomyBudget = field(default_factory=AutonomyBudget)
    escalate_on: list[str] = field(default_factory=list)
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "allowed_surfaces": list(self.allowed_surfaces),
            "budget": {
                "max_cost": self.budget.max_cost,
                "max_resource": self.budget.max_resource,
                "max_steps": self.budget.max_steps,
                "consumed_cost": self.budget.consumed_cost,
                "consumed_resource": self.budget.consumed_resource,
                "consumed_steps": self.budget.consumed_steps,
            },
            "escalate_on": list(self.escalate_on),
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class SafeStopSignal:
    """Fail-closed safe-stop signal emitted on a boundary violation.

    Defined by TASK-067 because the Kill Switch (T068) is not yet available.
    The same signal can later be forwarded to T068's emergency stop.
    """

    signal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal: str = ""
    loop: str = ""
    reason: str = ""
    violated_action: str = ""
    context_level: str = ""
    evidence_ref: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "goal": self.goal,
            "loop": self.loop,
            "reason": self.reason,
            "violated_action": self.violated_action,
            "context_level": self.context_level,
            "evidence_ref": self.evidence_ref,
            "created_at": self.created_at,
        }
