"""TenantManager."""
from __future__ import annotations
from aios.tenancy.contracts import Tenant, TenantBoundary, TenantError, TenantStatus

class TenantManager:
    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}
    def create_tenant(self, name: str, boundary: TenantBoundary = TenantBoundary.SHARED) -> Tenant:
        if any(t.name == name for t in self._tenants.values()):
            raise TenantError(f"Tenant '{name}' already exists")
        t = Tenant(name=name, boundary=boundary)
        self._tenants[t.tenant_id] = t
        return t
    def get_tenant(self, tid: str) -> Tenant:
        if tid not in self._tenants: raise TenantError(f"Tenant {tid!r} not found")
        return self._tenants[tid]
    def list_tenants(self) -> list[Tenant]: return list(self._tenants.values())
    def suspend_tenant(self, tid: str) -> Tenant:
        t = self.get_tenant(tid); t.status = TenantStatus.SUSPENDED; return t
    def deactivate_tenant(self, tid: str) -> Tenant:
        t = self.get_tenant(tid); t.status = TenantStatus.DEACTIVATED; return t
    def check_boundary(self, tid: str, required: TenantBoundary) -> bool:
        t = self.get_tenant(tid)
        levels = {TenantBoundary.SHARED: 0, TenantBoundary.DEDICATED: 1, TenantBoundary.ISOLATED: 2}
        return levels[t.boundary] >= levels[required]
