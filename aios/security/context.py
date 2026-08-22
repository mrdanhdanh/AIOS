"""Security context (TASK-070 — Security Baseline 1.0).

A :class:`SecurityContext` carries the *identity* and *authorization state* of
an external entry / capability / tool invocation. Secrets are stored **only** as
scoped references (``secret_refs``) — never as plaintext values — so they can
never be logged or leaked through this object.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SecurityContext:
    """Identity + authorization state for a secured action.

    Fields
    ------
    principal
        The authenticated subject (agent / service / user).
    scopes
        Granted scope labels (least-privilege). An action requesting a scope
        not present here is BLOCKed.
    permissions
        ``capability/tool -> allowed actions`` map (cached view of the grants
        held in the Runtime PermissionBroker for ``principal``).
    secret_refs
        Scoped references to secrets (e.g. ``{"db": "secret://db/main"}``).
        **Values are never stored here.**
    evidence_ref
        Optional reference to the audit/evidence record that established this
        context.
    authenticated
        Whether the context passed external authentication.
    """

    principal: str
    scopes: List[str] = field(default_factory=list)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    secret_refs: Dict[str, str] = field(default_factory=dict)
    evidence_ref: Optional[str] = None
    authenticated: bool = False

    def has_permission(self, target: str, action: str) -> bool:
        """Local (cached) permission check — informational."""
        allowed = self.permissions.get(target)
        if allowed is None:
            return False
        return action in allowed or "*" in allowed

    def in_scope(self, scope: str) -> bool:
        """Return True if ``scope`` is granted to this context."""
        return scope in self.scopes or "*" in self.scopes

    def secret_ref(self, name: str) -> Optional[str]:
        """Return the scoped secret reference for ``name`` (never the value)."""
        return self.secret_refs.get(name)

    def to_dict(self) -> Dict[str, Any]:
        # NOTE: secret_refs are refs only — no values are ever serialized.
        return {
            "principal": self.principal,
            "scopes": list(self.scopes),
            "permissions": {k: list(v) for k, v in self.permissions.items()},
            "secret_refs": {k: v for k, v in self.secret_refs.items()},
            "evidence_ref": self.evidence_ref,
            "authenticated": self.authenticated,
        }
