"""Identity contracts — Principal, Role, Permission, Policy."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class IdentityError(Exception): pass

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    DELETE = "delete"

@dataclass
class Role:
    role_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    permissions: set = field(default_factory=set)
    description: str = ""
    def has_permission(self, perm: Permission) -> bool: return perm in self.permissions
    def to_dict(self) -> dict[str, Any]:
        return {"role_id": self.role_id, "name": self.name, "permissions": sorted(p.value for p in self.permissions)}

@dataclass
class Principal:
    principal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str = ""
    roles: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    tenant_id: str = ""
    def effective_permissions(self) -> set:
        perms = set()
        for role in self.roles:
            perms.update(role.permissions)
        return perms
    def to_dict(self) -> dict[str, Any]:
        return {"principal_id": self.principal_id, "name": self.name, "roles": [r.to_dict() for r in self.roles], "tenant_id": self.tenant_id}

@dataclass
class Policy:
    policy_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    required_permission: Permission = Permission.READ
    effect: str = "allow"
    conditions: dict = field(default_factory=dict)
    def evaluate(self, principal: Principal) -> bool:
        if self.effect == "deny": return False
        for k, v in self.conditions.items():
            if principal.attributes.get(k) != v: return False
        return True
    def to_dict(self) -> dict[str, Any]:
        return {"policy_id": self.policy_id, "name": self.name, "effect": self.effect}
