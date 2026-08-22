"""ABAC authorization engine — Subject/Resource/Action/Environment evaluation.

Returns an AuthorizationDecision (ALLOW / DENY / ASK) with reason + provenance.
Fail-closed: ASK is never treated as allowed by default.
"""

from __future__ import annotations

from aios.identity.contracts import (
    AuthorizationDecision,
    AuthorizationRequest,
    Decision,
    Permission,
    Policy,
    Principal,
)


class AuthorizationEngine:
    """Evaluates authorization requests against RBAC + ABAC policies."""

    def __init__(self) -> None:
        self._policies: list[Policy] = []

    def add_policy(self, policy: Policy) -> None:
        self._policies.append(policy)

    def evaluate(self, request: AuthorizationRequest) -> AuthorizationDecision:
        subject = request.subject
        if subject is None:
            return AuthorizationDecision(
                decision=Decision.DENY,
                reason="no_subject",
                provenance=["abac:no_subject"],
            )

        # RBAC baseline: subject must hold the action permission.
        rbac_ok = request.action in subject.effective_permissions()

        applicable = [p for p in self._policies if p.required_permission == request.action]

        # Explicit deny wins.
        for pol in applicable:
            if pol.effect == "deny" and not pol.evaluate(subject):
                return AuthorizationDecision(
                    decision=Decision.DENY,
                    reason=f"denied_by_policy:{pol.name}",
                    policy_id=pol.policy_id,
                    provenance=["abac:policy_deny", pol.policy_id],
                )

        # Explicit allow.
        for pol in applicable:
            if pol.effect == "allow" and pol.evaluate(subject):
                return AuthorizationDecision(
                    decision=Decision.ALLOW,
                    reason=f"allowed_by_policy:{pol.name}",
                    policy_id=pol.policy_id,
                    provenance=["abac:policy_allow", pol.policy_id],
                )

        # No policy: fall back to RBAC grant, else ASK (escalate).
        if rbac_ok:
            return AuthorizationDecision(
                decision=Decision.ALLOW,
                reason="rbac_fallback",
                provenance=["abac:rbac_fallback"],
            )
        return AuthorizationDecision(
            decision=Decision.ASK,
            reason="no_matching_policy_and_no_rbac_grant",
            provenance=["abac:ask"],
        )
