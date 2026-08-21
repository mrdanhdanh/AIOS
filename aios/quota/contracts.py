"""Quota contracts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Quota:
    tenant_id: str = ""
    resource_type: str = ""
    limit: int = 100
    used: int = 0
    @property
    def remaining(self) -> int: return max(0, self.limit - self.used)
    @property
    def exceeded(self) -> bool: return self.used >= self.limit
    def to_dict(self) -> dict[str, Any]:
        return {"tenant_id": self.tenant_id, "resource_type": self.resource_type, "limit": self.limit, "used": self.used}

@dataclass
class QuotaUsage:
    tenant_id: str = ""
    resource_type: str = ""
    used: int = 0
    limit: int = 0
    def to_dict(self) -> dict[str, Any]:
        return {"tenant_id": self.tenant_id, "resource_type": self.resource_type, "used": self.used, "limit": self.limit}
