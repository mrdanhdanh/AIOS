"""Multi-tenancy (M7 — TASK-036)."""
from aios.tenancy.contracts import Tenant, TenantBoundary, TenantError, TenantStatus
from aios.tenancy.tenant_manager import TenantManager
__all__ = ["Tenant", "TenantBoundary", "TenantError", "TenantStatus", "TenantManager"]
