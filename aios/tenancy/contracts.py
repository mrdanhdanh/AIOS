"""Tenancy contracts."""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class TenantError(Exception): pass

class TenantStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"

class TenantBoundary(Enum):
    SHARED = "shared"
    DEDICATED = "dedicated"
    ISOLATED = "isolated"

class TenantScope(str, Enum):
    ORGANIZATION = "organization"
    TENANT = "tenant"
    PROJECT = "project"
    WORKSPACE = "workspace"

@dataclass
class Organization:
    org_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"org_id": self.org_id, "name": self.name}

@dataclass
class Project:
    project_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    tenant_id: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"project_id": self.project_id, "name": self.name, "tenant_id": self.tenant_id}

@dataclass
class Workspace:
    workspace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    project_id: str = ""
    tenant_id: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"workspace_id": self.workspace_id, "name": self.name, "project_id": self.project_id, "tenant_id": self.tenant_id}

@dataclass
class TenantContext:
    """Resolved tenant scope for an operation (INV-023)."""
    tenant_id: str = ""
    organization_id: str = ""
    project_id: str = ""
    workspace_id: str = ""
    scope: TenantScope = TenantScope.TENANT
    def to_dict(self) -> dict[str, Any]:
        return {"tenant_id": self.tenant_id, "organization_id": self.organization_id, "project_id": self.project_id, "workspace_id": self.workspace_id, "scope": self.scope.value}

@dataclass
class TenantResource:
    """A resource owned by a tenant (for isolation enforcement)."""
    resource_id: str = ""
    tenant_id: str = ""
    kind: str = ""
    def to_dict(self) -> dict[str, Any]:
        return {"resource_id": self.resource_id, "tenant_id": self.tenant_id, "kind": self.kind}

@dataclass
class TenantIsolationPolicy:
    """Policy describing allowed cross-tenant access."""
    policy_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    allow_cross_tenant: bool = False
    allowed_tenant_ids: list[str] = field(default_factory=list)
    def permits(self, a: str, b: str) -> bool:
        if a == b:
            return True
        if self.allow_cross_tenant:
            return True
        return b in self.allowed_tenant_ids

@dataclass
class Tenant:
    tenant_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    status: TenantStatus = TenantStatus.ACTIVE
    boundary: TenantBoundary = TenantBoundary.SHARED
    organization_id: str = ""
    project: str = ""
    workspace: str = ""
    config: dict = field(default_factory=dict)
    @property
    def is_active(self) -> bool: return self.status == TenantStatus.ACTIVE
    def to_dict(self) -> dict[str, Any]:
        return {"tenant_id": self.tenant_id, "name": self.name, "status": self.status.value, "boundary": self.boundary.value, "organization_id": self.organization_id, "project": self.project, "workspace": self.workspace}
