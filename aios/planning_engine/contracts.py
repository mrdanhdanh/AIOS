"""Planning engine contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlanStatus(str, Enum):
    DRAFT = "draft"
    VALID = "valid"
    INVALID = "invalid"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DependencyType(str, Enum):
    HARD = "hard"
    SOFT = "soft"


@dataclass
class GoalAnalysis:
    goal_text: str = ""
    goal_type: str = ""
    complexity: str = "medium"
    required_capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"goal_text": self.goal_text, "goal_type": self.goal_type, "complexity": self.complexity, "required_capabilities": self.required_capabilities}


@dataclass
class PlanStep:
    step_id: str = ""
    name: str = ""
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.HARD
    required_capabilities: list[str] = field(default_factory=list)
    estimated_tokens: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"step_id": self.step_id, "name": self.name, "dependencies": self.dependencies, "dependency_type": self.dependency_type.value, "required_capabilities": self.required_capabilities, "risk_level": self.risk_level.value}


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings}


@dataclass
class ExecutionPlan:
    plan_id: str = ""
    goal: GoalAnalysis | None = None
    steps: list[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    total_estimated_tokens: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    validation: ValidationResult | None = None
    provenance: list[str] = field(default_factory=list)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def to_dict(self) -> dict[str, Any]:
        return {"plan_id": self.plan_id, "steps": [s.to_dict() for s in self.steps], "status": self.status.value, "step_count": self.step_count, "total_estimated_tokens": self.total_estimated_tokens}
