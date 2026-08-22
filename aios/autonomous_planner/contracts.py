"""Autonomous Planner contracts (TASK-051)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlanStatus(str, Enum):
    DRAFT = "draft"
    VALID = "valid"
    REJECTED = "rejected"
    EXECUTING = "executing"
    SUPERSEDED = "superseded"


class ReplanTrigger(str, Enum):
    """Conditions that activate a re-plan (spec §3)."""
    TASK_FAILED = "task_failed"
    DEPENDENCY_CHANGED = "dependency_changed"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    POLICY_CHANGED = "policy_changed"
    EXECUTION_DEVIATION = "execution_deviation"
    ASSUMPTION_INVALID = "assumption_invalid"
    PROGRESS_NOT_MET = "progress_not_met"
    MANUAL = "manual"


class ReplanSafety(str, Enum):
    """Re-planning safety classification (spec §6)."""
    SAFE_TO_REPLAN = "safe_to_replan"
    REPLAN_AFTER_CURRENT_TASK = "replan_after_current_task"
    REPLAN_AFTER_CHECKPOINT = "replan_after_checkpoint"
    REQUIRES_HUMAN_APPROVAL = "requires_human_approval"
    BLOCKED = "blocked"


@dataclass
class PlanTask:
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    description: str = ""
    depends_on: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    estimated_effort: str = ""
    side_effect: bool = False  # whether the task mutates external state

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "depends_on": list(self.depends_on),
            "required_capabilities": list(self.required_capabilities),
            "estimated_effort": self.estimated_effort,
            "side_effect": self.side_effect,
        }


@dataclass
class AutonomousPlan:
    goal_id: str = ""
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    version: int = 1
    objective: str = ""
    tasks: list[PlanTask] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    resource_estimate: dict[str, Any] = field(default_factory=dict)
    policy_requirements: list[str] = field(default_factory=list)
    success_conditions: list[str] = field(default_factory=list)
    replan_conditions: list[str] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    parent_plan_id: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "plan_id": self.plan_id,
            "version": self.version,
            "objective": self.objective,
            "tasks": [t.to_dict() for t in self.tasks],
            "dependencies": list(self.dependencies),
            "assumptions": list(self.assumptions),
            "risks": list(self.risks),
            "required_capabilities": list(self.required_capabilities),
            "resource_estimate": dict(self.resource_estimate),
            "policy_requirements": list(self.policy_requirements),
            "success_conditions": list(self.success_conditions),
            "replan_conditions": list(self.replan_conditions),
            "status": self.status.value,
            "parent_plan_id": self.parent_plan_id,
        }
