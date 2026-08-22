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

class PrincipalType(str, Enum):
    USER = "user"
    SERVICE = "service"
    AGENT = "agent"
    SYSTEM = "system"

class AuthSource(str, Enum):
    LOCAL = "local"
    OIDC = "oidc"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"

class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"

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
class Attribute:
    """An ABAC attribute (Subject/Resource/Action/Environment facet)."""
    key: str = ""
    value: Any = None
    category: str = "subject"  # subject | resource | action | environment

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "value": self.value, "category": self.category}

@dataclass
class Principal:
    principal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str = ""
    roles: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    tenant_id: str = ""
    principal_type: PrincipalType = PrincipalType.USER
    auth_source: AuthSource = AuthSource.LOCAL
    metadata: dict = field(default_factory=dict)
    def effective_permissions(self) -> set:
        perms = set()
        for role in self.roles:
            perms.update(role.permissions)
        return perms
    def to_dict(self) -> dict[str, Any]:
        return {"principal_id": self.principal_id, "name": self.name, "roles": [r.to_dict() for r in self.roles], "tenant_id": self.tenant_id, "principal_type": self.principal_type.value, "auth_source": self.auth_source.value}

@dataclass
class IdentityContext:
    """Carries the identity + environment for an authorization decision."""
    principal: Principal | None = None
    environment: dict = field(default_factory=dict)
    session_id: str = ""

@dataclass
class AuthorizationRequest:
    """Subject/Resource/Action/Environment authorization request (ABAC)."""
    subject: Principal | None = None
    resource: str = ""
    action: Permission = Permission.READ
    environment: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource": self.resource,
            "action": self.action.value,
            "environment": self.environment,
        }

@dataclass
class AuthorizationDecision:
    """An authorization decision with reason + provenance (fail-closed)."""
    decision: Decision = Decision.DENY
    reason: str = ""
    policy_id: str | None = None
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "policy_id": self.policy_id,
            "provenance": self.provenance,
        }

    @property
    def allowed(self) -> bool:
        # Fail-closed: ASK is NOT allowed by default.
        return self.decision == Decision.ALLOW

@dataclass
class Delegation:
    """A delegation with capability attenuation (delegatee <= delegator)."""
    delegation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    delegator_id: str = ""
    delegatee_id: str = ""
    permissions: set = field(default_factory=set)
    resource_scope: str = ""
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "delegation_id": self.delegation_id,
            "delegator_id": self.delegator_id,
            "delegatee_id": self.delegatee_id,
            "permissions": sorted(p.value for p in self.permissions),
            "resource_scope": self.resource_scope,
            "active": self.active,
        }

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
