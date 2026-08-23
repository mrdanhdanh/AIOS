"""TASK-199 — Coding Policy Engine (M26).

Policy engine for coding actions, converging Policy Engine (T177) and
Credential/Policy (T113). Deterministic, fail-closed, provenance-bearing.

Layering: ``coding_edition`` is an ``unknown`` (infra) layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from aios.coding_edition._common import CodingEditionError, _hash


class PolicyVerdict(str, Enum):
    """Policy evaluation outcome (T199)."""

    PASS = "PASS"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PolicyRule:
    """A single deterministic policy rule (T199)."""

    rule_id: str
    description: str
    required_capability: Optional[str] = None
    min_trust: float = 0.0

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise CodingEditionError("rule_id is required (T001 Rule 1, immutable).")


@dataclass
class PolicyContext:
    """Context evaluated against the policy set (T199)."""

    action: str
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    trust: float = 1.0
    evidence_ref: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.action:
            raise CodingEditionError("action is required.")


class PolicyEngine:
    """Deterministic coding policy engine (T199)."""

    def __init__(self, rules: Optional[List[PolicyRule]] = None) -> None:
        self._rules: List[PolicyRule] = list(rules or [])

    def add(self, rule: PolicyRule) -> None:
        self._rules.append(rule)

    def evaluate(self, ctx: PolicyContext) -> Tuple[PolicyVerdict, List[str]]:
        """Evaluate ``ctx`` against all rules (fail-closed, deterministic).

        Returns (verdict, violated_rule_ids). UNKNOWN is never promoted to PASS.
        """
        violated: List[str] = []
        for rule in self._rules:
            if rule.required_capability and rule.required_capability not in ctx.capabilities:
                violated.append(rule.rule_id)
                continue
            if ctx.trust < rule.min_trust:
                violated.append(rule.rule_id)
                continue
        if not self._rules:
            # No policy defined -> cannot assert sufficiency -> UNKNOWN.
            return PolicyVerdict.UNKNOWN, []
        if violated:
            return PolicyVerdict.INSUFFICIENT, violated
        return PolicyVerdict.PASS, []

    def verdict_hash(self, ctx: PolicyContext) -> str:
        v, _ = self.evaluate(ctx)
        return _hash(f"{ctx.action}|{v.value}|{','.join(ctx.capabilities)}|{ctx.trust}")
