"""Credential + Permission + Policy Integration (TASK-113, M17).

Integrates credential (secret), permission (RBAC/ABAC, T035) and policy into
every inference call, fail-closed. The credential **value is never stored in
logs or evidence** (T040). Missing permission/policy -> BLOCK (T078). The same
context + policy -> same decision (deterministic).

Layering: ``unknown`` (infra) layer. Integrates with ``aios.identity`` (T035),
``aios.security`` (T040) and the policy boundary declared by T109.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from aios.identity.contracts import (
    AuthorizationDecision,
    AuthorizationRequest,
    Decision,
    Permission,
    Principal,
)
from aios.security.contracts import Credential, CredentialType

from .contracts import ModelContract


__all__ = [
    "SecurityError",
    "SecurityContext",
    "CredentialBoundary",
    "PermissionCheck",
    "PolicyPrecheck",
    "SecurityGate",
]


class SecurityError(Exception):
    """Raised when a security invariant is violated (fail-closed, T078)."""


@dataclass
class SecurityContext:
    """A security-scoped inference context (no secret value leaked)."""

    principal: Principal
    credential_ref: str  # reference only — never the value (T040)
    permission_scope: str
    policy_decision: Decision = Decision.DENY
    inference_ref: str = ""
    evidence_ref: str = ""
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        # Explicitly excludes any credential value (T040).
        return {
            "principal_id": self.principal.principal_id,
            "credential_ref": self.credential_ref,
            "permission_scope": self.permission_scope,
            "policy_decision": self.policy_decision.value,
            "inference_ref": self.inference_ref,
            "evidence_ref": self.evidence_ref,
            "provenance": list(self.provenance),
        }


class CredentialBoundary:
    """Injects a credential reference without ever exposing its value (T040)."""

    @staticmethod
    def inject(credential: Credential) -> str:
        """Return a safe reference; the value is never returned or logged."""
        if not credential.is_valid():
            raise SecurityError("credential is invalid (fail-closed)")
        return f"cred-ref:{credential.cred_id}:{credential.cred_type.value}"

    @staticmethod
    def redact(value: str) -> str:
        """Redact any secret value that might appear in a log/evidence string."""
        if not value:
            return value
        return "***REDACTED***"


class PermissionCheck:
    """RBAC/ABAC permission check (T035)."""

    def __init__(
        self,
        *,
        abac_fn: Optional[Callable[[AuthorizationRequest], AuthorizationDecision]] = None,
    ) -> None:
        self._abac = abac_fn

    def check(
        self,
        principal: Principal,
        resource: str,
        action: Permission,
    ) -> AuthorizationDecision:
        # RBAC: effective permissions from roles.
        if action in principal.effective_permissions():
            decision = AuthorizationDecision(
                decision=Decision.ALLOW,
                reason="rbac:permission-granted",
                provenance=["model_runtime.security:rbac"],
            )
        else:
            decision = AuthorizationDecision(
                decision=Decision.DENY,
                reason="rbac:permission-missing",
                provenance=["model_runtime.security:rbac"],
            )
        # ABAC overlay (if provided) — deny wins (fail-closed).
        if self._abac is not None:
            req = AuthorizationRequest(
                subject=principal, resource=resource, action=action
            )
            overlay = self._abac(req)
            if overlay.decision == Decision.DENY:
                decision = overlay
        return decision


class PolicyPrecheck:
    """Policy decision before execution (T004/T005)."""

    def __init__(self, *, policy_fn: Optional[Callable[[str, str], bool]] = None) -> None:
        # policy_fn(policy_ref, resource) -> allowed
        self._policy_fn = policy_fn

    def decide(self, policy_ref: str, resource: str) -> Decision:
        if not policy_ref:
            # No policy required -> allow (open boundary).
            return Decision.ALLOW
        if self._policy_fn is None:
            # Without an explicit policy engine, a required policy that cannot be
            # evaluated is treated as DENY (fail-closed, T078).
            return Decision.DENY
        allowed = self._policy_fn(policy_ref, resource)
        return Decision.ALLOW if allowed else Decision.DENY


class SecurityGate:
    """Fail-closed gate combining credential + permission + policy (T113)."""

    def __init__(
        self,
        *,
        permission_check: Optional[PermissionCheck] = None,
        policy_precheck: Optional[PolicyPrecheck] = None,
        producer: str = "model_runtime.security",
    ) -> None:
        self._perm = permission_check or PermissionCheck()
        self._policy = policy_precheck or PolicyPrecheck()
        self._producer = producer

    def authorize(
        self,
        principal: Principal,
        credential: Credential,
        *,
        resource: str = "inference",
        action: Permission = Permission.EXECUTE,
        policy_ref: str = "",
        inference_ref: str = "",
        run_id: str = "security",
    ) -> SecurityContext:
        # 1. Credential boundary — inject reference only (T040).
        cred_ref = CredentialBoundary.inject(credential)
        # 2. Permission check (T035).
        perm_decision = self._perm.check(principal, resource, action)
        if perm_decision.decision != Decision.ALLOW:
            ctx = SecurityContext(
                principal=principal,
                credential_ref=cred_ref,
                permission_scope=resource,
                policy_decision=Decision.DENY,
                inference_ref=inference_ref,
            )
            ctx.provenance.append(
                f"{self._producer}:permission-denied:{perm_decision.reason}:{run_id}"
            )
            return ctx
        # 3. Policy pre-check (T004/T005) — fail-closed.
        policy_decision = self._policy.decide(policy_ref, resource)
        ctx = SecurityContext(
            principal=principal,
            credential_ref=cred_ref,
            permission_scope=resource,
            policy_decision=policy_decision,
            inference_ref=inference_ref,
        )
        ctx.provenance.append(
            f"{self._producer}:policy-{policy_decision.value}:{run_id}"
        )
        return ctx

    @staticmethod
    def is_authorized(context: SecurityContext) -> bool:
        return context.policy_decision == Decision.ALLOW
