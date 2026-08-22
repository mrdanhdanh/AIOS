"""Autonomy Governor engine (TASK-054).

Gates every autonomous action before execution. Fail-closed: any uncertainty
(policy / risk / scope / permission / budget / approval) → BLOCK.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aios.autonomy_governor.contracts import (
    ApprovalRequest,
    AutonomyAction,
    AutonomyBudget,
    AutonomyDecision,
    AutonomyMode,
    AutonomyPolicy,
    AutonomyRisk,
)

# Base risk weight per action (deterministic, no LLM).
_ACTION_RISK: dict[AutonomyAction, float] = {
    AutonomyAction.READ: 0.1,
    AutonomyAction.WRITE: 0.3,
    AutonomyAction.EXECUTE: 0.4,
    AutonomyAction.NETWORK: 0.4,
    AutonomyAction.CREDENTIAL: 0.7,
    AutonomyAction.INSTALL: 0.7,
    AutonomyAction.MODIFY_SYSTEM: 0.8,
    AutonomyAction.DESTRUCTIVE: 1.0,
    AutonomyAction.POLICY_ESCALATION: 0.7,
}

_RISK_LEVELS = [AutonomyRisk.LOW, AutonomyRisk.MEDIUM, AutonomyRisk.HIGH, AutonomyRisk.CRITICAL]
_RISK_THRESHOLDS = [0.25, 0.5, 0.75]  # LOW<0.25<=MEDIUM<0.5<=HIGH<0.75<=CRITICAL


@dataclass
class ActionContext:
    action: AutonomyAction
    target: str = ""
    scope: dict[str, Any] = field(default_factory=dict)  # allowed scope
    resource_estimate: dict[str, Any] = field(default_factory=dict)
    privilege_required: bool = False
    reversible: bool = True
    approval: ApprovalRequest | None = None


class AutonomyGovernor:
    def __init__(
        self,
        policy: AutonomyPolicy | None = None,
        budget: AutonomyBudget | None = None,
        allowed_scope: dict[str, Any] | None = None,
    ) -> None:
        self._policy = policy or AutonomyPolicy(mode=AutonomyMode.SUPERVISED)
        self._budget = budget or AutonomyBudget()
        self._scope = allowed_scope or {}
        self._last_reason: str = ""

    # ---- classification -------------------------------------------------
    def classify_action(self, action_str: str) -> AutonomyAction:
        try:
            return AutonomyAction(action_str.lower())
        except ValueError:
            # Unknown action → treat as highest-risk (fail-closed).
            return AutonomyAction.DESTRUCTIVE

    # ---- risk scoring ---------------------------------------------------
    def score_risk(self, ctx: ActionContext) -> tuple[AutonomyRisk, float]:
        score = _ACTION_RISK.get(ctx.action, 1.0)
        # resource risk
        est = ctx.resource_estimate or {}
        if isinstance(est.get("cost"), (int, float)) and float(est["cost"]) > 0.5:
            score += 0.1
        # target risk: external/unknown target is riskier
        if ctx.target and ctx.target.startswith("external:"):
            score += 0.1
        # privilege risk
        if ctx.privilege_required:
            score += 0.15
        # reversibility risk: irreversible actions add risk
        if not ctx.reversible:
            score += 0.2
        # cumulative risk
        score += min(0.3, self._budget.cumulative_risk * 0.1)
        score = min(1.0, score)
        level = AutonomyRisk.LOW
        for i, thr in enumerate(_RISK_THRESHOLDS):
            if score >= thr:
                level = _RISK_LEVELS[i + 1]
        return level, score

    # ---- scope ----------------------------------------------------------
    def check_scope(self, ctx: ActionContext) -> bool:
        scope = self._scope or {}
        allowed_targets = scope.get("targets") or scope.get("files") or []
        if allowed_targets and ctx.target and ctx.target not in allowed_targets:
            # Allow prefix match for workspace-style scopes.
            if not any(ctx.target.startswith(str(t)) for t in allowed_targets):
                return False
        allowed_caps = scope.get("capabilities")
        if allowed_caps is not None and ctx.action.value not in allowed_caps:
            return False
        return True

    # ---- budget ---------------------------------------------------------
    def check_budget(self) -> bool:
        return self._budget.within_limits()

    def consume(self, ctx: ActionContext, risk_score: float) -> None:
        self._budget.steps += 1
        self._budget.tool_calls += 1
        est = ctx.resource_estimate or {}
        if isinstance(est.get("cost"), (int, float)):
            self._budget.cost += float(est["cost"])
        if isinstance(est.get("tokens"), (int, float)):
            self._budget.tokens += int(est["tokens"])
        self._budget.cumulative_risk += risk_score

    # ---- decision -------------------------------------------------------
    def decide(self, ctx: ActionContext) -> AutonomyDecision:
        # 0. Disabled mode blocks everything.
        if self._policy.mode == AutonomyMode.DISABLED:
            self._last_reason = "autonomy disabled"
            return AutonomyDecision.BLOCK
        # 1. Action policy rule.
        rule = self._policy.action_rule(ctx.action)
        if rule == "deny":
            self._last_reason = f"action {ctx.action.value} denied by policy"
            return AutonomyDecision.BLOCK
        # 2. Scope boundary.
        if not self.check_scope(ctx):
            self._last_reason = "action outside allowed scope"
            return AutonomyDecision.BLOCK if self._policy.mode != AutonomyMode.AUTONOMOUS else AutonomyDecision.ASK
        # 3. Budget.
        if not self.check_budget():
            self._last_reason = "autonomy budget exceeded"
            return AutonomyDecision.BLOCK
        # 4. Risk.
        level, score = self.score_risk(ctx)
        if level == AutonomyRisk.CRITICAL and self._policy.mode != AutonomyMode.AUTONOMOUS:
            if ctx.approval is not None and ctx.approval.is_valid():
                self._last_reason = "critical action with valid approval"
                return AutonomyDecision.ALLOW
            self._last_reason = "critical action requires approval"
            return AutonomyDecision.ASK
        # 5. Action rule "ask".
        if rule == "ask":
            if ctx.approval is not None and ctx.approval.is_valid():
                self._last_reason = "approved"
                return AutonomyDecision.ALLOW
            self._last_reason = f"action {ctx.action.value} requires approval"
            return AutonomyDecision.ASK
        # 6. Fail-closed default.
        if rule not in ("allow",):
            self._last_reason = "uncertain policy → fail-closed"
            return AutonomyDecision.BLOCK
        self._last_reason = "allowed"
        return AutonomyDecision.ALLOW

    def request_approval(self, ctx: ActionContext, reason: str, risk: AutonomyRisk) -> ApprovalRequest:
        return ApprovalRequest(
            goal=ctx.scope.get("goal", ""),
            action=ctx.action.value,
            target=ctx.target,
            reason=reason,
            risk=risk,
            requested_permissions=[ctx.action.value],
            resource_estimate=ctx.resource_estimate or {},
            expected_side_effect="mutates target" if not ctx.reversible else "none",
            rollback_strategy="checkpoint" if not ctx.reversible else "n/a",
            evidence=ctx.scope.get("evidence", []),
        )

    @property
    def last_reason(self) -> str:
        return self._last_reason

    @property
    def budget(self) -> AutonomyBudget:
        return self._budget

    def state(self) -> dict[str, Any]:
        """Read-only snapshot of current autonomy governance state.

        Used by the observability dashboard (TASK-072) to render the AUTONOMY
        view. This is a pure projection — it never mutates policy, budget, or
        scope, and is safe to call from a read-only surface.
        """
        return {
            "mode": self._policy.mode.value,
            "policy": self._policy.to_dict(),
            "budget": self._budget.to_dict(),
            "scope": dict(self._scope),
            "last_reason": self._last_reason,
        }
