"""Permission scopes and a permission broker (TASK-004, M1).

Permissions gate *what a subject may do to a resource*. A :class:`Permission`
pairs a :class:`PermissionScope` (the verb) with a ``resource`` string; a
resource of ``"*"`` is a wildcard that matches any concrete resource.

The :class:`PermissionBroker` is the authority consulted by the policy engine
before any execution is allowed. It is deterministic and offline-first: pure
Python, no LLM, no external calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Set


__all__ = ["PermissionScope", "Permission", "PermissionBroker"]


class PermissionScope(Enum):
    """The verbs a subject may be granted."""

    EXECUTE = "execute"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    CAPABILITY_INVOKE = "capability:invoke"
    TOOL_INVOKE = "tool:invoke"
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"


@dataclass(frozen=True)
class Permission:
    """A single grant: ``scope`` on ``resource`` (``"*"`` = wildcard)."""

    scope: PermissionScope
    resource: str = "*"

    def matches(self, scope: PermissionScope, resource: str) -> bool:
        if self.scope != scope:
            return False
        if self.resource == "*" or self.resource == resource:
            return True
        # Prefix wildcard: "workflow:*" grants "workflow:demo".
        if self.resource.endswith("*") and resource.startswith(self.resource[:-1]):
            return True
        return False

    def __str__(self) -> str:
        return f"{self.scope.value}:{self.resource}"


class PermissionBroker:
    """Grants and checks permissions for named subjects (agents, services)."""

    def __init__(self) -> None:
        self._grants: Dict[str, Set[Permission]] = {}

    def grant(self, subject: str, permission: Permission) -> None:
        self._grants.setdefault(subject, set()).add(permission)

    def grant_many(self, subject: str, permissions: Iterable[Permission]) -> None:
        for p in permissions:
            self.grant(subject, p)

    def revoke(self, subject: str, permission: Permission) -> None:
        grants = self._grants.get(subject)
        if grants:
            grants.discard(permission)

    def has(self, subject: str, scope: PermissionScope, resource: str) -> bool:
        """Return True if *subject* holds ``scope`` on ``resource`` (wildcard ok)."""
        for p in self._grants.get(subject, set()):
            if p.matches(scope, resource):
                return True
        return False

    def check(self, subject: str, scope: PermissionScope, resource: str) -> bool:
        """Alias of :meth:`has` (explicit, readable at call sites)."""
        return self.has(subject, scope, resource)

    def list_for(self, subject: str) -> List[Permission]:
        return sorted(
            self._grants.get(subject, set()), key=lambda p: (p.scope.value, p.resource)
        )

    def subjects(self) -> List[str]:
        return sorted(self._grants.keys())
