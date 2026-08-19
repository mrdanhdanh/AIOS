"""Deterministic policy pre-check (TASK-004, M1 — Rule 4).

The policy decision is computed **before** any execution is permitted. The fast
path is purely deterministic: permission checks plus an ordered rule table.
No LLM is invoked on the fast path. When the deterministic path cannot reach a
decisive verdict it returns ``INSUFFICIENT`` so the caller (the decision
pipeline in a later task) can escalate to an LLM planner — but this module
never calls the LLM itself, preserving the deterministic-first invariant.

Layering: this module is at the ``runtime`` layer and only depends on
``aios.core`` and sibling runtime modules (relative imports), never on
agent/orchestrator layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

from .permission import PermissionBroker, PermissionScope


__all__ = [
    "PolicyDecision",
    "PolicyRequest",
    "PolicyRule",
    "PolicyResult",
    "PolicyEngine",
]


class PolicyDecision(Enum):
    """Outcome of a policy evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    INSUFFICIENT = "insufficient"  # deterministic path cannot decide; escalate


@dataclass
class PolicyRequest:
    """A request presented to the policy engine for pre-check."""

    subject: str
    action: str
    resource: str
    context_id: Optional[str] = None
    scope: Optional[PermissionScope] = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class PolicyRule:
    """A single deterministic policy rule."""

    rule_id: str
    applies: Callable[["PolicyRequest"], bool]
    decision: PolicyDecision
    reason: str = ""


@dataclass
class PolicyResult:
    """The computed policy decision plus traceability."""

    decision: PolicyDecision
    reason: str
    applied_rules: List[str] = field(default_factory=list)


class PolicyEngine:
    """Evaluates policy pre-checks deterministically.

    Evaluation order for a request:
      1. If a ``scope`` is present, the subject MUST hold that permission for the
         resource, else ``DENY`` (fail-closed).
      2. Rules are evaluated in registration order. The first matching ``DENY``
         wins immediately. A matching ``ALLOW`` is recorded but does not stop
         evaluation (so a later DENY can still override).
      3. If only ``ALLOW`` rules matched -> ``ALLOW``.
      4. If nothing matched -> ``INSUFFICIENT`` (escalate out-of-band).
    """

    def __init__(self, broker: Optional[PermissionBroker] = None) -> None:
        self._rules: List[PolicyRule] = []
        self._broker = broker or PermissionBroker()

    @property
    def broker(self) -> PermissionBroker:
        return self._broker

    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)

    def clear_rules(self) -> None:
        self._rules.clear()

    def evaluate(self, request: PolicyRequest) -> PolicyResult:
        # 1) Permission gate (fail-closed).
        if request.scope is not None and not self._broker.has(
            request.subject, request.scope, request.resource
        ):
            return PolicyResult(
                PolicyDecision.DENY,
                f"subject {request.subject!r} lacks permission "
                f"{request.scope.value} on {request.resource!r}",
                [],
            )

        # 2) Rule table.
        applied: List[str] = []
        allowed = False
        for rule in self._rules:
            if rule.applies(request):
                applied.append(rule.rule_id)
                if rule.decision == PolicyDecision.DENY:
                    return PolicyResult(PolicyDecision.DENY, rule.reason or "denied", applied)
                if rule.decision == PolicyDecision.ALLOW:
                    allowed = True

        if allowed:
            return PolicyResult(PolicyDecision.ALLOW, "allowed by policy", applied)
        return PolicyResult(
            PolicyDecision.INSUFFICIENT,
            "no decisive policy rule matched; escalate",
            applied,
        )

    @classmethod
    def deny_all(cls, broker: Optional[PermissionBroker] = None) -> "PolicyEngine":
        """Convenience engine that denies everything deterministically."""
        eng = cls(broker=broker)
        eng.add_rule(
            PolicyRule(
                "deny-all",
                applies=lambda r: True,
                decision=PolicyDecision.DENY,
                reason="default deny",
            )
        )
        return eng

    @classmethod
    def allow_all(cls, broker: Optional[PermissionBroker] = None) -> "PolicyEngine":
        """Convenience engine that allows everything deterministically."""
        eng = cls(broker=broker)
        eng.add_rule(
            PolicyRule(
                "allow-all",
                applies=lambda r: True,
                decision=PolicyDecision.ALLOW,
                reason="default allow",
            )
        )
        return eng
