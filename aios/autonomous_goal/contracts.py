"""Autonomous goal contracts."""
from __future__ import annotations
import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class GoalStatus(Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class GoalState(str, Enum):
    """Canonical autonomous-goal lifecycle (spec T050)."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class Objective:
    """A sub-goal / objective within a goal."""
    objective_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    parent_id: str = ""
    done: bool = False
    def to_dict(self) -> dict[str, Any]:
        return {"objective_id": self.objective_id, "title": self.title, "parent_id": self.parent_id, "done": self.done}

@dataclass
class GoalEvidence:
    """Evidence linking a goal action to its provenance."""
    evidence_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    action: str = ""
    provenance: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"evidence_id": self.evidence_id, "goal_id": self.goal_id, "action": self.action, "provenance": self.provenance}

@dataclass
class Goal:
    goal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    status: GoalStatus = GoalStatus.CREATED
    state: GoalState = GoalState.DRAFT
    priority: int = 0
    objectives: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "status": self.status.value,
            "state": self.state.value,
            "objectives": [o.to_dict() for o in self.objectives],
        }

@dataclass
class GoalPlan:
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    goal_id: str = ""
    steps: list = field(default_factory=list)
    estimated_effort: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"plan_id": self.plan_id, "goal_id": self.goal_id, "steps": self.steps}
