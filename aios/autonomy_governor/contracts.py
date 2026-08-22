"""Autonomy Governor contracts (TASK-054)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AutonomyMode(str, Enum):
    DISABLED = "disabled"
    SUPERVISED = "supervised"
    BOUNDED = "bounded"
    AUTONOMOUS = "autonomous"


class AutonomyAction(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    CREDENTIAL = "credential"
    INSTALL = "install"
    MODIFY_SYSTEM = "modify_system"
    DESTRUCTIVE = "destructive"
    POLICY_ESCALATION = "policy_escalation"


class AutonomyRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutonomyDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    ASK = "ask"


@dataclass
class AutonomyBudget:
    """Tracks an autonomous run's consumed budget vs limits."""
    max_steps: int = 20
    max_runtime_seconds: float = 1800.0
    max_cost: float = 1.0
    max_tool_calls: int = 50
    max_tokens: int = 100000
    max_retries: int = 5
    steps: int = 0
    tool_calls: int = 0
    runtime_seconds: float = 0.0
    cost: float = 0.0
    tokens: int = 0
    retries: int = 0
    cumulative_risk: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_steps": self.max_steps, "max_runtime_seconds": self.max_runtime_seconds,
            "max_cost": self.max_cost, "max_tool_calls": self.max_tool_calls,
            "max_tokens": self.max_tokens, "max_retries": self.max_retries,
            "steps": self.steps, "tool_calls": self.tool_calls,
            "runtime_seconds": self.runtime_seconds, "cost": self.cost,
            "tokens": self.tokens, "retries": self.retries,
            "cumulative_risk": self.cumulative_risk,
        }

    def within_limits(self) -> bool:
        return (
            self.steps <= self.max_steps
            and self.tool_calls <= self.max_tool_calls
            and self.runtime_seconds <= self.max_runtime_seconds
            and self.cost <= self.max_cost
            and self.tokens <= self.max_tokens
            and self.retries <= self.max_retries
        )


@dataclass
class AutonomyPolicy:
    mode: AutonomyMode = AutonomyMode.SUPERVISED
    limits: dict[str, float] = field(default_factory=dict)
    # action -> "allow" | "ask" | "deny"
    actions: dict[str, str] = field(default_factory=dict)
    approval: dict[str, str] = field(default_factory=dict)

    def action_rule(self, action: AutonomyAction) -> str:
        return self.actions.get(action.value, "ask")

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "limits": dict(self.limits),
            "actions": dict(self.actions),
            "approval": dict(self.approval),
        }


@dataclass
class ApprovalRequest:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal: str = ""
    action: str = ""
    target: str = ""
    reason: str = ""
    risk: AutonomyRisk = AutonomyRisk.LOW
    requested_permissions: list[str] = field(default_factory=list)
    resource_estimate: dict[str, Any] = field(default_factory=dict)
    expected_side_effect: str = ""
    rollback_strategy: str = ""
    evidence: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600.0)
    used: bool = False

    def is_valid(self) -> bool:
        return (not self.used) and (time.time() <= self.expires_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id, "goal": self.goal, "action": self.action,
            "target": self.target, "risk": self.risk.value,
            "requested_permissions": list(self.requested_permissions),
            "evidence": list(self.evidence), "used": self.used,
        }
