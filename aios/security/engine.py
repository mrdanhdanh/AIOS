"""Security baseline engine (TASK-070 — Security Baseline 1.0).

Ties together authentication, authorization (Runtime PermissionBroker +
PolicyEngine), least-privilege scoping, optional Autonomy Governor scope
enforcement, and audit. The engine is **deterministic**: the same
``(SecurityContext, target, action, scope)`` tuple always yields the same
:class:`SecurityDecision`.

Fail-closed everywhere: missing auth, missing permission, or exceeded scope →
BLOCK. No default-allow.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from aios.autonomy_governor.contracts import AutonomyAction
from aios.autonomy_governor.governor import ActionContext, AutonomyGovernor
from aios.security.audit import SecurityAudit
from aios.security.auth import AuthError, AuthValidator
from aios.security.broker import SecurityPermissionBroker
from aios.security.context import SecurityContext
from aios.security.secrets import SecretStore


@dataclass
class SecurityDecision:
    """The outcome of a security check."""

    allowed: bool
    reason: str
    audit_id: Optional[str] = None
    evidence_ref: Optional[str] = None

    @property
    def blocked(self) -> bool:
        return not self.allowed


class SecurityBaseline:
    """Security baseline 1.0 — auth + authz + least-privilege + audit.

    Integration points (downward/peer imports only, no ``agents``):
      * ``aios.runtime.permission`` / ``aios.runtime.policy``  (T054/Policy)
      * ``aios.autonomy_governor``                              (T054)
      * ``aios.api.auth`` (via :mod:`aios.security.api_bridge`) (API)
    """

    def __init__(
        self,
        auth: Optional[AuthValidator] = None,
        broker: Optional[SecurityPermissionBroker] = None,
        audit: Optional[SecurityAudit] = None,
        secrets: Optional[SecretStore] = None,
        governor: Optional[AutonomyGovernor] = None,
        require_auth: bool = True,
    ) -> None:
        self._auth = auth or AuthValidator()
        self._broker = broker or SecurityPermissionBroker()
        self._audit = audit or SecurityAudit()
        self._secrets = secrets or SecretStore()
        self._governor = governor
        self._require_auth = require_auth

    # ---- external entry auth ------------------------------------------- #
    def authenticate(self, token: Optional[str]) -> SecurityContext:
        """Authenticate an external caller. Fail-closed (raises on no auth)."""
        if self._require_auth:
            return self._auth.validate(token)
        # Auth disabled: accept a valid token, else anonymous (no privileges).
        try:
            return self._auth.validate(token)
        except AuthError:
            return SecurityContext(principal="anonymous", authenticated=False)

    # ---- main check ---------------------------------------------------- #
    def check(
        self,
        ctx: SecurityContext,
        target: str,
        action: str,
        scope: Optional[str] = None,
        privileged: bool = False,
    ) -> SecurityDecision:
        """Evaluate a secured action. Fail-closed → BLOCK on any gap.

        Order of gates (all deterministic):
          1. authentication state (if required)
          2. permission broker (Runtime Permission + Policy)
          3. least-privilege scope (``ctx.in_scope``)
          4. optional Autonomy Governor target-scope enforcement
        A privileged ALLOW still writes an audit evidence record.
        """
        # 1) auth
        if self._require_auth and not ctx.authenticated:
            return self._block(ctx, action, target, "authentication required")

        # 2) permission broker (fail-closed)
        if not self._broker.check(ctx.principal, target, action):
            return self._block(
                ctx, action, target,
                f"permission denied for {action!r} on {target!r}",
            )

        # 3) least-privilege scope
        if scope is not None and not ctx.in_scope(scope):
            return self._block(
                ctx, action, target,
                f"action exceeds granted scope {scope!r}",
            )

        # 4) optional governor target-scope enforcement
        gov_ok, gov_reason = self._governor_allows(ctx, target, action)
        if not gov_ok:
            return self._block(ctx, action, target, gov_reason)

        # ALLOW (audit privileged actions)
        decision = SecurityDecision(True, "allowed")
        if privileged:
            rec = self._audit.record(
                ctx.principal, action, target, "ALLOW",
                {"privileged": True, "scope": scope},
            )
            decision.audit_id = rec.audit_id
            decision.evidence_ref = rec.evidence_ref
        return decision

    # ---- internals ----------------------------------------------------- #
    def _block(
        self,
        ctx: SecurityContext,
        action: str,
        target: str,
        reason: str,
    ) -> SecurityDecision:
        self._audit.record(ctx.principal, action, target, "BLOCK", {"reason": reason})
        return SecurityDecision(False, reason)

    def _governor_allows(
        self, ctx: SecurityContext, target: str, action: str
    ) -> tuple[bool, str]:
        if self._governor is None:
            return True, ""
        g_action = self._governor.classify_action(self._map_action(action))
        g_ctx = ActionContext(action=g_action, target=target)
        # The governor enforces its configured allowed scope; align it with the
        # security context's granted scopes for this evaluation, then restore.
        original = self._governor._scope
        self._governor._scope = {"targets": list(ctx.scopes)}
        try:
            if not self._governor.check_scope(g_ctx):
                return False, f"governor blocks {action!r} on {target!r}"
        finally:
            self._governor._scope = original
        return True, ""

    @staticmethod
    def _map_action(action: str) -> str:
        a = (action or "").lower()
        if a.startswith("capability"):
            return AutonomyAction.EXECUTE.value
        if a.startswith("tool"):
            return AutonomyAction.EXECUTE.value
        if a in ("read", "get", "list", "fetch"):
            return AutonomyAction.READ.value
        if a in ("write", "create", "update", "set", "put"):
            return AutonomyAction.WRITE.value
        if a in ("delete", "remove", "destroy"):
            return AutonomyAction.DESTRUCTIVE.value
        if a in ("execute", "run", "exec"):
            return AutonomyAction.EXECUTE.value
        return AutonomyAction.EXECUTE.value
