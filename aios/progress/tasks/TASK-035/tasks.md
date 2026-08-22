# TASK-035 — Breakdown

## Steps
1. Create `aios/identity/contracts.py` — Principal (principal_id, name, roles, attributes, tenant_id), Role (role_id, name, permissions), Permission enum, Policy (policy_id, name, required_permission, effect, conditions)
2. Create `aios/identity/identity_service.py` — IdentityService: resolve principal, build IdentityContext, authorize with Policy evaluation
3. Create `aios/identity/rbac.py` — RBAC resolver: role → permission resolution, deny-by-default
4. Implement ABAC: Subject/Resource/Action/Environment evaluation via Policy conditions
5. Implement Delegation: scope restriction, expiration, provenance, capability attenuation
6. Create `aios/identity/tests/` — 7 tests (principal, roles, permissions, policy evaluation, delegation, fail-closed, architecture)
7. Run architecture guard — verify no Agent → Identity/Role/Policy storage direct access
8. Run full suite — 1763/1763 PASS (7 new), no regressions

## Dependencies
- TASK-034 Doctor + Readiness

## Exit Criteria
- All AC-035-01..12 PASS, gate PASS, no regressions
