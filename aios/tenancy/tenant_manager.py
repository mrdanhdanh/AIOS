"""TenantManager."""
from __future__ import annotations

from aios.tenancy.contracts import (
    Organization,
    Project,
    Tenant,
    TenantBoundary,
    TenantContext,
    TenantError,
    TenantIsolationPolicy,
    TenantResource,
    TenantScope,
    TenantStatus,
    Workspace,
)


class TenantManager:
    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}
        self._orgs: dict[str, Organization] = {}
        self._projects: dict[str, Project] = {}
        self._workspaces: dict[str, Workspace] = {}
        self._isolation = TenantIsolationPolicy()

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

    # --- Organization / Project / Workspace ---
    def create_organization(self, name: str) -> Organization:
        org = Organization(name=name)
        self._orgs[org.org_id] = org
        return org

    def create_project(self, name: str, tenant_id: str) -> Project:
        self.get_tenant(tenant_id)
        proj = Project(name=name, tenant_id=tenant_id)
        self._projects[proj.project_id] = proj
        return proj

    def create_workspace(self, name: str, project_id: str) -> Workspace:
        proj = self._projects.get(project_id)
        if proj is None:
            raise TenantError(f"Project {project_id!r} not found")
        ws = Workspace(name=name, project_id=project_id, tenant_id=proj.tenant_id)
        self._workspaces[ws.workspace_id] = ws
        return ws

    def resolve_scope(self, tenant_id: str, project_id: str = "", workspace_id: str = "") -> TenantContext:
        """Resolve a tenant scope context (INV-023)."""
        t = self.get_tenant(tenant_id)
        scope = TenantScope.TENANT
        if workspace_id and workspace_id in self._workspaces:
            scope = TenantScope.WORKSPACE
        elif project_id and project_id in self._projects:
            scope = TenantScope.PROJECT
        return TenantContext(
            tenant_id=tenant_id,
            organization_id=t.organization_id,
            project_id=project_id,
            workspace_id=workspace_id,
            scope=scope,
        )

    def assert_same_tenant(self, a: str, b: str) -> None:
        """Fail-closed: raise on cross-tenant access unless isolation policy permits."""
        if a == b:
            return
        if not self._isolation.permits(a, b):
            raise TenantError(f"Cross-tenant access denied: {a} -> {b}")

    def authorize(self, ctx: TenantContext, resource: TenantResource) -> bool:
        """Authorize a tenant context against a resource (tenant isolation)."""
        if ctx.tenant_id == resource.tenant_id:
            return True
        return self._isolation.permits(ctx.tenant_id, resource.tenant_id)

    def filter_by_tenant(self, items: list[TenantResource], tenant_id: str) -> list[TenantResource]:
        """Return only resources owned by the given tenant."""
        return [r for r in items if r.tenant_id == tenant_id]
