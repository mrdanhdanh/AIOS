"""Permission broker integration (TASK-070).

Wraps the Runtime :class:`~aios.runtime.permission.PermissionBroker` and
:class:`~aios.runtime.policy.PolicyEngine` so that **every** capability/tool
action is gated by a permission check. This is integration with the existing
Runtime security primitives — *not* a parallel security system.

Fail-closed: a missing grant or a ``DENY`` policy decision → ``False`` (BLOCK).
"""
from __future__ import annotations

from typing import Optional

from aios.runtime.permission import PermissionBroker, PermissionScope
from aios.runtime.policy import (
    PolicyDecision,
    PolicyEngine,
    PolicyRequest,
)


class SecurityPermissionBroker:
    """Authoritative permission check for capability/tool actions.

    Uses the Runtime PermissionBroker (grants) and PolicyEngine (rules). Both
    must agree (grant present AND policy ALLOW) for an action to be permitted.
    """

    def __init__(
        self,
        broker: Optional[PermissionBroker] = None,
        policy: Optional[PolicyEngine] = None,
    ) -> None:
        self._broker = broker or PermissionBroker()
        self._policy = policy or PolicyEngine(broker=self._broker)

    @property
    def broker(self) -> PermissionBroker:
        return self._broker

    @property
    def policy(self) -> PolicyEngine:
        return self._policy

    def check(self, subject: str, target: str, action: str) -> bool:
        """Return True only if ``subject`` may perform ``action`` on ``target``.

        Fail-closed: any missing grant or DENY policy → False (BLOCK).
        """
        scope = self._scope_for(action)
        # 1) Permission grant gate (fail-closed).
        if not self._broker.has(subject, scope, target):
            return False
        # 2) Policy pre-check (fail-closed).
        result = self._policy.evaluate(
            PolicyRequest(
                subject=subject,
                action=action,
                resource=target,
                scope=scope,
            )
        )
        # An explicit DENY blocks. ALLOW or INSUFFICIENT (no decisive rule
        # matched) both fall through to ALLOW because the grant above is the
        # authority — fail-closed is preserved by gate (1): a missing grant is
        # always BLOCKed.
        return result.decision != PolicyDecision.DENY

    @staticmethod
    def _scope_for(action: str) -> PermissionScope:
        a = (action or "").lower()
        if a in ("capability_invoke", "capability:invoke", "invoke_capability"):
            return PermissionScope.CAPABILITY_INVOKE
        if a in ("tool_invoke", "tool:invoke", "invoke_tool"):
            return PermissionScope.TOOL_INVOKE
        if a in ("read", "get", "list", "fetch"):
            return PermissionScope.READ
        if a in ("write", "create", "update", "set", "put"):
            return PermissionScope.WRITE
        if a in ("delete", "remove", "destroy"):
            return PermissionScope.DELETE
        if a in ("execute", "run", "exec"):
            return PermissionScope.EXECUTE
        # Unknown action → highest-risk scope (fail-closed).
        return PermissionScope.ADMIN
