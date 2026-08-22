"""Plan validation (spec §5). A plan must pass contract / dependency /
capability / permission / policy / resource / risk validation before execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aios.autonomous_planner.contracts import AutonomousPlan, PlanTask


class ValidationStage(str, Enum):
    CONTRACT = "contract"
    DEPENDENCY = "dependency"
    CAPABILITY = "capability"
    PERMISSION = "permission"
    POLICY = "policy"
    RESOURCE = "resource"
    RISK = "risk"
    EXECUTION_GRAPH = "execution_graph"


@dataclass
class PlanValidationResult:
    valid: bool = True
    stage: ValidationStage = ValidationStage.CONTRACT
    errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def add_error(self, stage: ValidationStage, msg: str) -> None:
        self.valid = False
        self.stage = stage
        self.errors.append(f"[{stage.value}] {msg}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "stage": self.stage.value,
            "errors": list(self.errors),
            "details": dict(self.details),
        }


class PlanValidator:
    """Deterministic validation of an AutonomousPlan."""

    def __init__(
        self,
        available_capabilities: list[str] | None = None,
        granted_permissions: list[str] | None = None,
        allowed_policies: list[str] | None = None,
        resource_budget: dict[str, float] | None = None,
        max_risk_level: str = "critical",
    ) -> None:
        self.available_capabilities = set(available_capabilities or [])
        self.granted_permissions = set(granted_permissions or [])
        self.allowed_policies = set(allowed_policies or [])
        self.resource_budget = dict(resource_budget or {})
        self.max_risk_level = max_risk_level

    def validate(self, plan: AutonomousPlan) -> PlanValidationResult:
        res = PlanValidationResult()
        self._validate_contract(plan, res)
        if not res.valid:
            return res
        self._validate_dependency(plan, res)
        if not res.valid:
            return res
        self._validate_capability(plan, res)
        self._validate_permission(plan, res)
        self._validate_policy(plan, res)
        self._validate_resource(plan, res)
        self._validate_risk(plan, res)
        self._validate_execution_graph(plan, res)
        if res.valid:
            res.details["task_count"] = len(plan.tasks)
        return res

    def _validate_contract(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        if not plan.goal_id:
            res.add_error(ValidationStage.CONTRACT, "plan.goal_id is required")
        if not plan.objective:
            res.add_error(ValidationStage.CONTRACT, "plan.objective is required")
        if not plan.tasks:
            res.add_error(ValidationStage.CONTRACT, "plan.tasks must not be empty")
        for t in plan.tasks:
            if not t.name:
                res.add_error(ValidationStage.CONTRACT, f"task {t.task_id} missing name")

    def _validate_dependency(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        ids = {t.task_id for t in plan.tasks}
        for t in plan.tasks:
            for dep in t.depends_on:
                if dep not in ids:
                    res.add_error(
                        ValidationStage.DEPENDENCY,
                        f"task {t.task_id} depends on unknown task {dep}",
                    )

    def _validate_capability(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        for cap in plan.required_capabilities:
            if cap not in self.available_capabilities:
                res.add_error(
                    ValidationStage.CAPABILITY,
                    f"required capability {cap!r} is not available",
                )
        for t in plan.tasks:
            for cap in t.required_capabilities:
                if cap not in self.available_capabilities:
                    res.add_error(
                        ValidationStage.CAPABILITY,
                        f"task {t.task_id} requires unavailable capability {cap!r}",
                    )

    def _validate_permission(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        for t in plan.tasks:
            if t.side_effect and "write" not in self.granted_permissions:
                res.add_error(
                    ValidationStage.PERMISSION,
                    f"task {t.task_id} has side effects but write permission not granted",
                )

    def _validate_policy(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        for p in plan.policy_requirements:
            if p not in self.allowed_policies:
                res.add_error(
                    ValidationStage.POLICY,
                    f"policy requirement {p!r} is not allowed",
                )

    def _validate_resource(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        est = plan.resource_estimate or {}
        for key, limit in self.resource_budget.items():
            used = est.get(key)
            if used is not None and isinstance(used, (int, float)):
                if float(used) > float(limit):
                    res.add_error(
                        ValidationStage.RESOURCE,
                        f"estimated {key}={used} exceeds budget {limit}",
                    )

    def _validate_risk(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        levels = ["low", "medium", "high", "critical"]
        max_idx = levels.index(self.max_risk_level) if self.max_risk_level in levels else 3
        for risk in plan.risks:
            # risks are free-form strings; only enforce if prefixed with level:
            if ":" in risk:
                lvl = risk.split(":", 1)[0].lower()
                if lvl in levels and levels.index(lvl) > max_idx:
                    res.add_error(
                        ValidationStage.RISK,
                        f"risk level {lvl} exceeds max allowed {self.max_risk_level}",
                    )

    def _validate_execution_graph(self, plan: AutonomousPlan, res: PlanValidationResult) -> None:
        # A plan must be compilable to a DAG (no cycles among tasks).
        adj: dict[str, list[str]] = {t.task_id: list(t.depends_on) for t in plan.tasks}
        visited: dict[str, int] = {}

        def has_cycle(node: str) -> bool:
            if node in visited:
                return visited[node] == 1
            visited[node] = 1
            for nxt in adj.get(node, []):
                if has_cycle(nxt):
                    return True
            visited[node] = 2
            return False

        for n in adj:
            if has_cycle(n):
                res.add_error(
                    ValidationStage.EXECUTION_GRAPH,
                    "plan tasks contain a dependency cycle (not compilable to DAG)",
                )
                return
