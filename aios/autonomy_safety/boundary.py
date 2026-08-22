"""Autonomy Boundary Check (TASK-067).

Every action within a goal/loop's ``AutonomyContext`` is checked via the
Autonomy Governor (T054) boundary. Out-of-boundary actions are BLOCKed
(fail-closed). This module is a *safety layer* — it delegates all authority to
the Governor and never re-implements governor logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from aios.autonomy_governor.contracts import (
    AutonomyAction,
    AutonomyBudget as GovBudget,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
)
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor
from aios.autonomy_safety.contracts import (
    AutonomyContext,
    AutonomyLevel,
    SafeStopSignal,
    SafetyDecision,
)
from aios.autonomy_safety.safe_stop import SafeStopPolicy


# Map an autonomy level to the Governor mode used for its boundary checks.
_LEVEL_TO_MODE = {
    AutonomyLevel.L0: AutonomyMode.SUPERVISED,
    AutonomyLevel.L1: AutonomyMode.SUPERVISED,
    AutonomyLevel.L2: AutonomyMode.BOUNDED,
    AutonomyLevel.L3: AutonomyMode.AUTONOMOUS,
    AutonomyLevel.L4: AutonomyMode.AUTONOMOUS,
}


def _build_governor(context: AutonomyContext) -> AutonomyGovernor:
    """Construct a Governor that enforces this context's boundary.

    The boundary is expressed as the set of allowed surfaces (capabilities) and
    the context budget. The Governor remains the sole authority.
    """
    mode = _LEVEL_TO_MODE.get(context.level, AutonomyMode.SUPERVISED)
    actions = {surface: "allow" for surface in context.allowed_surfaces}
    policy = AutonomyPolicy(mode=mode, actions=actions)
    scope = {"capabilities": list(context.allowed_surfaces)}
    budget = GovBudget(
        max_cost=context.budget.max_cost,
        max_steps=context.budget.max_steps,
        cost=context.budget.consumed_cost,
        tokens=0,
        steps=context.budget.consumed_steps,
    )
    return AutonomyGovernor(policy=policy, allowed_scope=scope, budget=budget)


@dataclass
class BoundaryResult:
    decision: SafetyDecision
    governor_decision: AutonomyDecision
    reason: str
    action: str = ""
    level: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "governor_decision": self.governor_decision.value,
            "reason": self.reason,
            "action": self.action,
            "level": self.level,
        }


def check_boundary(
    context: AutonomyContext,
    action: str,
    target: str = "",
    **kwargs: Any,
) -> BoundaryResult:
    """Check an action against the goal/loop's autonomy boundary via Governor.

    Returns ``ALLOW`` only when the Governor explicitly allows; any other
    Governor outcome (BLOCK or ASK) is mapped to ``BLOCK`` — fail-closed for
    autonomous execution (an action that needs approval cannot proceed on its
    own).
    """
    gov = _build_governor(context)
    act = gov.classify_action(action)
    ctx = ActionContext(action=act, target=target, **kwargs)
    gd = gov.decide(ctx)
    decision = SafetyDecision.ALLOW if gd == AutonomyDecision.ALLOW else SafetyDecision.BLOCK
    return BoundaryResult(
        decision=decision,
        governor_decision=gd,
        reason=gov.last_reason,
        action=action,
        level=context.level.value,
    )


def _risk_class_of(context: AutonomyContext, action: str, target: str = "", **kwargs: Any) -> str:
    """Determine the Governor risk class string for an action."""
    gov = _build_governor(context)
    act = gov.classify_action(action)
    ctx = ActionContext(action=act, target=target, **kwargs)
    level, _ = gov.score_risk(ctx)
    return level.value


@dataclass
class EvaluationResult:
    decision: SafetyDecision
    boundary: BoundaryResult
    signal: Optional[SafeStopSignal] = None
    risk_class: str = ""
    escalated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "boundary": self.boundary.to_dict(),
            "risk_class": self.risk_class,
            "escalated": self.escalated,
            "signal": self.signal.to_dict() if self.signal else None,
        }


def evaluate_action(
    context: AutonomyContext,
    action: str,
    target: str = "",
    goal: str = "",
    loop: str = "",
    safe_stop: Optional[SafeStopPolicy] = None,
    **kwargs: Any,
) -> EvaluationResult:
    """Full autonomy-safety evaluation of an action.

    1. Boundary check via Governor. On BLOCK -> fail-closed SAFE_STOP.
    2. If allowed, check ``escalate_on`` risk classes -> ESCALATE.
    3. Otherwise ALLOW.
    """
    boundary = check_boundary(context, action, target=target, **kwargs)
    if boundary.decision == SafetyDecision.BLOCK:
        ss = safe_stop or SafeStopPolicy()
        signal = ss.trigger(
            context=context,
            action=action,
            reason=boundary.reason,
            goal=goal,
            loop=loop,
        )
        return EvaluationResult(
            decision=SafetyDecision.SAFE_STOP,
            boundary=boundary,
            signal=signal,
        )

    risk_class = _risk_class_of(context, action, target=target, **kwargs)
    if risk_class in [r.lower() for r in context.escalate_on]:
        return EvaluationResult(
            decision=SafetyDecision.ESCALATE,
            boundary=boundary,
            risk_class=risk_class,
            escalated=True,
        )

    return EvaluationResult(
        decision=SafetyDecision.ALLOW,
        boundary=boundary,
        risk_class=risk_class,
    )
