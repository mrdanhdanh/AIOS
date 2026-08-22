# TASK-036 — Breakdown

## Steps
1. Create `aios/tenancy/contracts.py` — Tenant (tenant_id, name, status, boundary, config), TenantStatus, TenantBoundary
2. Create `aios/tenancy/tenant_manager.py` — TenantManager: create_tenant, get_tenant, list_tenants, enforce boundary (cross-tenant DENY)
3. Implement tenant-scoped resource ownership and context propagation
4. Implement memory isolation: tenant namespace, tenant-aware retrieval/ranking/filtering
5. Implement audit with tenant identity for boundary violations
6. Create `aios/tenancy/tests/` — 5 tests (create, active check, boundary, isolation, fail-closed)
7. Run architecture guard — verify no cross-tenant bypass
8. Run full suite — 1768/1768 PASS (5 new), no regressions

## Dependencies
- TASK-035 Identity

## Exit Criteria
- All AC-036-01..14 PASS, gate PASS, no regressions
