"""TASK-177 — Policy Engine + Profiles + Precedence (M24).

Evaluates policies for a scope with a profile and precedence. Fail-closed:
no applicable policy -> BLOCKED (deny by default); ambiguous precedence tie -> BLOCKED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aios.quality_gate._common import QualityGateError, _hash

PROFILES = ("STRICT", "BALANCED", "PERMISSIVE")
DECISIONS = ("ALLOW", "DENY", "BLOCKED")


@dataclass(frozen=True)
class Policy:
    policy_id: str
    scope: str
    decision: str  # ALLOW | DENY
    precedence: int  # higher overrides lower

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise QualityGateError("policy_id must be non-empty")
        if not self.scope:
            raise QualityGateError("scope must be non-empty")
        if self.decision not in ("ALLOW", "DENY"):
            raise QualityGateError(f"invalid decision: {self.decision}")


@dataclass(frozen=True)
class PolicyReport:
    report_id: str
    scope: str
    decision: str
    applied: tuple


class PolicyEngine:
    """Evaluate policies for a scope with profile + precedence."""

    def __init__(self, profile: str = "BALANCED") -> None:
        if profile not in PROFILES:
            raise QualityGateError(f"invalid profile: {profile}")
        self.profile = profile

    def evaluate(self, scope: str, policies: List[Policy]) -> PolicyReport:
        if not scope:
            raise QualityGateError("scope must be non-empty")
        if policies is None:
            raise QualityGateError("policies must be provided")
        applicable = [p for p in policies if p.scope == scope]
        for p in applicable:
            if not isinstance(p, Policy):
                raise QualityGateError("each policy must be a Policy")
        if not applicable:
            # No policy -> fail-closed to BLOCKED (deny by default).
            report_id = _hash(f"{scope}|BLOCKED|none")
            return PolicyReport(report_id=report_id, scope=scope, decision="BLOCKED", applied=())
        # Precedence: highest precedence wins; ties -> BLOCKED (ambiguous).
        top = max(applicable, key=lambda p: p.precedence)
        ties = [p for p in applicable if p.precedence == top.precedence]
        decision = "BLOCKED" if len(ties) > 1 else top.decision
        report_id = _hash(f"{scope}|{decision}|{','.join(sorted(p.policy_id for p in applicable))}")
        return PolicyReport(report_id=report_id, scope=scope, decision=decision, applied=tuple(applicable))
