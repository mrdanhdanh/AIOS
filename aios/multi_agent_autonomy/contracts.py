"""Multi-Agent Autonomy (Delegation) contracts (TASK-059)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DelegationVerdict(str, Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    ASK_HUMAN = "ask_human"


@dataclass
class Authority:
    """Multi-dimensional authority (not a scalar budget)."""
    capabilities: set[str] = field(default_factory=set)
    resource_budget: float = 0.0  # token/cost ceiling
    deadline: float = 0.0  # seconds from now
    tenant_scope: str = ""
    tool_permissions: set[str] = field(default_factory=set)
    approval_required: bool = False
    max_depth: int = 0  # remaining delegation depth
    risk_level: str = "low"

    def to_dict(self) -> dict[str, Any]:
        return {
            "capabilities": sorted(self.capabilities),
            "resource_budget": self.resource_budget,
            "deadline": self.deadline,
            "tenant_scope": self.tenant_scope,
            "tool_permissions": sorted(self.tool_permissions),
            "approval_required": self.approval_required,
            "max_depth": self.max_depth,
            "risk_level": self.risk_level,
        }


@dataclass
class DelegateRequest:
    parent_goal_id: str = ""
    sub_goal: str = ""
    attenuated_authority: Authority | None = None
    delegation_budget: float = 0.0  # quota to delegate further downstream
    execution_budget: float = 0.0  # resource for the child
    max_depth: int = 0
    max_children: int = 0
    evidence_ref: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "parent_goal_id": self.parent_goal_id,
            "sub_goal": self.sub_goal,
            "delegation_budget": self.delegation_budget,
            "execution_budget": self.execution_budget,
            "max_depth": self.max_depth,
            "max_children": self.max_children,
        }


@dataclass
class DelegateResponse:
    child_agent_id: str = ""
    sub_goal_result: str = ""
    authority_used: Authority | None = None
    resource_used: float = 0.0
    evidence_ref: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "child_agent_id": self.child_agent_id,
            "sub_goal_result": self.sub_goal_result,
            "resource_used": self.resource_used,
            "evidence_ref": self.evidence_ref,
        }


@dataclass
class DelegationDecision:
    verdict: DelegationVerdict
    reason: str = ""
    child_authority: Authority | None = None
    request: DelegateRequest | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "reason": self.reason,
            "child_authority": self.child_authority.to_dict() if self.child_authority else None,
        }
