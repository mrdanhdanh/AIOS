"""Planning Engine — transforms goals into execution plans.

AC-026-01: Goal → multi-step execution plan.
AC-026-09: Deterministic planning first.
AC-026-04: Cycles detected and rejected.
AC-026-13: Invalid plan not handed to Runtime.
"""

from __future__ import annotations

import hashlib
from typing import Any

from aios.planning_engine.contracts import (
    DependencyType,
    ExecutionPlan,
    GoalAnalysis,
    PlanStatus,
    PlanStep,
    RiskLevel,
    ValidationResult,
)


class PlanningEngine:
    """Transforms goals into validated execution plans."""

    def __init__(self) -> None:
        self._plans: list[ExecutionPlan] = []

    def analyze_goal(self, goal_text: str) -> GoalAnalysis:
        """Analyze a goal and extract structure."""
        capabilities = []
        complexity = "low"
        if "build" in goal_text.lower() or "create" in goal_text.lower():
            capabilities.append("code_generation")
            complexity = "medium"
        if "test" in goal_text.lower():
            capabilities.append("test_generation")
        if "deploy" in goal_text.lower():
            capabilities.append("deployment")
            complexity = "high"
        if not capabilities:
            capabilities.append("general")

        return GoalAnalysis(
            goal_text=goal_text,
            goal_type="task",
            complexity=complexity,
            required_capabilities=capabilities,
        )

    def decompose(self, analysis: GoalAnalysis) -> list[PlanStep]:
        """Decompose goal into plan steps."""
        steps = []
        step_id = "step-1"
        steps.append(PlanStep(
            step_id=step_id,
            name="analyze",
            description=f"Analyze requirements for: {analysis.goal_text}",
            required_capabilities=analysis.required_capabilities[:1],
            estimated_tokens=500,
        ))

        if analysis.complexity in ("medium", "high"):
            steps.append(PlanStep(
                step_id="step-2",
                name="implement",
                description="Implement solution",
                dependencies=[step_id],
                required_capabilities=analysis.required_capabilities,
                estimated_tokens=2000,
                risk_level=RiskLevel.MEDIUM,
            ))

        if analysis.complexity == "high":
            steps.append(PlanStep(
                step_id="step-3",
                name="validate",
                description="Validate implementation",
                dependencies=["step-2"],
                required_capabilities=["test_generation"],
                estimated_tokens=1000,
            ))

        return steps

    def detect_cycles(self, steps: list[PlanStep]) -> list[str]:
        """Detect dependency cycles using DFS."""
        graph: dict[str, list[str]] = {s.step_id: list(s.dependencies) for s in steps}
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for dep in graph.get(node, []):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    cycles.append(f"{node} → {dep}")
                    return True
            rec_stack.discard(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node)
        return cycles

    def validate(self, plan: ExecutionPlan) -> ValidationResult:
        """Validate an execution plan."""
        errors: list[str] = []
        warnings: list[str] = []

        # Check for steps
        if not plan.steps:
            errors.append("Plan has no steps")

        # Check for cycles
        cycles = self.detect_cycles(plan.steps)
        if cycles:
            errors.append(f"Cycles detected: {cycles}")

        # Check for missing dependencies
        step_ids = {s.step_id for s in plan.steps}
        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append(f"Step {step.step_id} depends on unknown step {dep}")

        # Check for self-loops
        for step in plan.steps:
            if step.step_id in step.dependencies:
                errors.append(f"Self-loop detected in step {step.step_id}")

        valid = len(errors) == 0
        return ValidationResult(valid=valid, errors=errors, warnings=warnings)

    def create_plan(self, goal_text: str) -> ExecutionPlan:
        """Full pipeline: analyze → decompose → validate."""
        plan_id = hashlib.sha256(goal_text.encode()).hexdigest()[:12]
        analysis = self.analyze_goal(goal_text)
        steps = self.decompose(analysis)

        # Compute totals
        total_tokens = sum(s.estimated_tokens for s in steps)
        max_risk = max((s.risk_level.value for s in steps), default="low")

        plan = ExecutionPlan(
            plan_id=plan_id,
            goal=analysis,
            steps=steps,
            total_estimated_tokens=total_tokens,
            risk_level=RiskLevel(max_risk),
            provenance=[f"planning_engine:{plan_id}"],
        )

        validation = self.validate(plan)
        plan.validation = validation
        plan.status = PlanStatus.VALID if validation.valid else PlanStatus.INVALID

        self._plans.append(plan)
        return plan

    def list_plans(self) -> list[ExecutionPlan]:
        return list(self._plans)
