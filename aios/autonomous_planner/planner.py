"""Autonomous Planner engine (TASK-051).

Deterministic-first planning: prefer existing workflow / known template /
rule-based planning / previous valid plan adaptation before falling back to an
LLM planner. The LLM is never the default path.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from aios.autonomous_planner.contracts import (
    AutonomousPlan,
    PlanStatus,
    PlanTask,
    ReplanSafety,
    ReplanTrigger,
)
from aios.autonomous_planner.validation import PlanValidationResult, PlanValidator


class PlanningStrategy(str, Enum):
    EXISTING_WORKFLOW = "existing_workflow"
    KNOWN_TEMPLATE = "known_template"
    RULE_BASED = "rule_based"
    PREVIOUS_PLAN = "previous_plan"
    LLM_PLANNER = "llm_planner"


@dataclass
class PlannerContext:
    """Observations the planner uses to generate / update a plan (spec §2.1)."""
    goal_id: str = ""
    goal_state: dict[str, Any] = field(default_factory=dict)
    completed_tasks: list[str] = field(default_factory=list)
    pending_tasks: list[str] = field(default_factory=list)
    failed_tasks: list[str] = field(default_factory=list)
    execution_history: list[dict[str, Any]] = field(default_factory=list)
    world_state: dict[str, Any] = field(default_factory=dict)
    available_capabilities: list[str] = field(default_factory=list)
    resource_constraints: dict[str, Any] = field(default_factory=dict)
    policy_constraints: list[str] = field(default_factory=list)
    previous_plan: AutonomousPlan | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ReplanDecision:
    trigger: ReplanTrigger
    safety: ReplanSafety
    reason: str
    new_plan: AutonomousPlan | None = None


class AutonomousPlanner:
    """Dynamic, deterministic-first autonomous planner."""

    def __init__(self, validator: PlanValidator | None = None) -> None:
        self._validator = validator or PlanValidator()
        self._templates: dict[str, AutonomousPlan] = {}
        self._llm_call_count = 0

    # ---- planning -------------------------------------------------------
    def plan(
        self,
        objective: str,
        context: PlannerContext,
        llm_planner: Callable[[str, PlannerContext], AutonomousPlan] | None = None,
    ) -> AutonomousPlan:
        """Generate a plan using the deterministic-first strategy ladder."""
        strategy, plan = self._try_deterministic(objective, context)
        if plan is None:
            if llm_planner is None:
                # Deterministic-only mode: build a rule-based skeleton.
                plan = self._rule_based_plan(objective, context)
                strategy = PlanningStrategy.RULE_BASED
            else:
                plan = llm_planner(objective, context)
                self._llm_call_count += 1
                strategy = PlanningStrategy.LLM_PLANNER
        plan.objective = objective
        plan.goal_id = context.goal_id
        result = self._validator_for_context(context).validate(plan)
        plan.status = PlanStatus.VALID if result.valid else PlanStatus.REJECTED
        plan._strategy = strategy  # type: ignore[attr-defined]
        return plan

    def _validator_for_context(self, context: PlannerContext) -> PlanValidator:
        """Build a validator reflecting the runtime context (capabilities,
        permissions, budget, policy)."""
        budget = {}
        for k, v in (context.resource_constraints or {}).items():
            if isinstance(v, (int, float)):
                budget[k] = v
        return PlanValidator(
            available_capabilities=list(context.available_capabilities or []),
            granted_permissions=list(context.policy_constraints or ["read", "write"]),
            allowed_policies=list(context.policy_constraints or []),
            resource_budget=budget,
        )

    def _try_deterministic(
        self, objective: str, context: PlannerContext
    ) -> tuple[PlanningStrategy | None, AutonomousPlan | None]:
        # 1. existing workflow
        if objective in self._templates:
            tpl = self._templates[objective]
            plan = self._adapt_template(tpl, context)
            return PlanningStrategy.EXISTING_WORKFLOW, plan
        # 2. known template by keyword
        for key, tpl in self._templates.items():
            if key and key in objective.lower():
                return PlanningStrategy.KNOWN_TEMPLATE, self._adapt_template(tpl, context)
        # 3. previous valid plan adaptation
        if context.previous_plan is not None and context.previous_plan.status == PlanStatus.VALID:
            return PlanningStrategy.PREVIOUS_PLAN, self._adapt_previous(context.previous_plan, context)
        return None, None

    def _rule_based_plan(self, objective: str, context: PlannerContext) -> AutonomousPlan:
        steps = ["analyze", "implement", "verify"]
        tasks = [
            PlanTask(name=s, required_capabilities=list(context.available_capabilities[:1]))
            for s in steps
        ]
        # chain dependencies
        for i in range(1, len(tasks)):
            tasks[i].depends_on = [tasks[i - 1].task_id]
        return AutonomousPlan(
            goal_id=context.goal_id,
            objective=objective,
            tasks=tasks,
            required_capabilities=list(context.available_capabilities),
            assumptions=["objective is well-formed"],
            risks=["unknown complexity"],
            success_conditions=["all tasks completed"],
            replan_conditions=["task_failed", "progress_not_met"],
        )

    def _adapt_template(self, tpl: AutonomousPlan, context: PlannerContext) -> AutonomousPlan:
        plan = AutonomousPlan(
            goal_id=context.goal_id,
            objective=tpl.objective,
            tasks=[PlanTask(name=t.name, description=t.description,
                            required_capabilities=list(t.required_capabilities),
                            side_effect=t.side_effect) for t in tpl.tasks],
            required_capabilities=list(tpl.required_capabilities),
            assumptions=list(tpl.assumptions),
            risks=list(tpl.risks),
            success_conditions=list(tpl.success_conditions),
            replan_conditions=list(tpl.replan_conditions),
        )
        return plan

    def _adapt_previous(self, prev: AutonomousPlan, context: PlannerContext) -> AutonomousPlan:
        plan = AutonomousPlan(
            goal_id=context.goal_id,
            objective=prev.objective,
            tasks=[PlanTask(name=t.name, description=t.description,
                            depends_on=list(t.depends_on),
                            required_capabilities=list(t.required_capabilities),
                            side_effect=t.side_effect) for t in prev.tasks],
            required_capabilities=list(prev.required_capabilities),
            assumptions=list(prev.assumptions),
            risks=list(prev.risks),
            success_conditions=list(prev.success_conditions),
            replan_conditions=list(prev.replan_conditions),
            parent_plan_id=prev.plan_id,
        )
        return plan

    def register_template(self, key: str, plan: AutonomousPlan) -> None:
        self._templates[key] = plan

    # ---- replanning -----------------------------------------------------
    def should_replan(self, trigger: ReplanTrigger, context: PlannerContext) -> bool:
        return True

    def classify_replan_safety(
        self,
        trigger: ReplanTrigger,
        context: PlannerContext,
        running_task_id: str | None = None,
        checkpoint_available: bool = False,
        autonomy_level: str = "supervised",
    ) -> ReplanSafety:
        """Classify re-planning safety (spec §6)."""
        if trigger in (ReplanTrigger.POLICY_CHANGED, ReplanTrigger.CAPABILITY_UNAVAILABLE):
            if autonomy_level != "autonomous":
                return ReplanSafety.REQUIRES_HUMAN_APPROVAL
        if trigger == ReplanTrigger.EXECUTION_DEVIATION:
            return ReplanSafety.REPLAN_AFTER_CURRENT_TASK
        if trigger in (ReplanTrigger.DEPENDENCY_CHANGED, ReplanTrigger.ASSUMPTION_INVALID):
            return ReplanSafety.REPLAN_AFTER_CHECKPOINT if checkpoint_available else ReplanSafety.REPLAN_AFTER_CURRENT_TASK
        if trigger == ReplanTrigger.MANUAL:
            return ReplanSafety.REQUIRES_HUMAN_APPROVAL
        return ReplanSafety.SAFE_TO_REPLAN

    def replan(
        self,
        trigger: ReplanTrigger,
        context: PlannerContext,
        llm_planner: Callable[[str, PlannerContext], AutonomousPlan] | None = None,
    ) -> ReplanDecision:
        safety = self.classify_replan_safety(trigger, context)
        if safety == ReplanSafety.BLOCKED:
            return ReplanDecision(trigger, safety, "replan blocked by safety policy", None)
        if safety == ReplanSafety.REQUIRES_HUMAN_APPROVAL:
            return ReplanDecision(trigger, safety, "replan requires human approval", None)
        new_plan = self.plan(context.goal_state.get("objective", ""), context, llm_planner)
        new_plan.version = (context.previous_plan.version if context.previous_plan else 0) + 1
        new_plan.parent_plan_id = context.previous_plan.plan_id if context.previous_plan else ""
        if context.previous_plan is not None:
            context.previous_plan.status = PlanStatus.SUPERSEDED
        return ReplanDecision(trigger, safety, "replan generated", new_plan)

    # ---- introspection --------------------------------------------------
    @property
    def llm_call_count(self) -> int:
        return self._llm_call_count

    def validate(self, plan: AutonomousPlan) -> PlanValidationResult:
        return self._validator.validate(plan)
