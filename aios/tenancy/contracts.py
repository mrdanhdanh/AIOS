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

@dataclass
class Tenant:
    tenant_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    status: TenantStatus = TenantStatus.ACTIVE
    boundary: TenantBoundary = TenantBoundary.SHARED
    config: dict = field(default_factory=dict)
    @property
    def is_active(self) -> bool: return self.status == TenantStatus.ACTIVE
    def to_dict(self) -> dict[str, Any]:
        return {"tenant_id": self.tenant_id, "name": self.name, "status": self.status.value, "boundary": self.boundary.value}
