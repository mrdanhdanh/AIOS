# TASK-035 — Identity + Principal + RBAC/ABAC

## Objective
Build the Identity & Authorization Foundation: Principal (User/Service/Agent/Workflow/System) → Tenant → Role/Attributes → Action → Resource → Policy → Decision (ALLOW/DENY/ASK). Provides identity context as input to Permission/Policy services with fail-closed semantics (INV-022 Identity First). No parallel control plane.

## Scope
### In scope
- Principal contract (5 types: User, Service, Agent, Workflow, System) with id, type, tenant_id, roles, attributes, metadata, auth_source
- IdentityContext and AuthorizationContext (principal, tenant, roles, attributes, resource, action, environment, delegation)
- RBAC: Role → Permission resolution, deny-by-default
- ABAC: Subject/Resource/Action/Environment evaluation, deterministic policy
- Delegation with scope restriction, expiration, provenance, capability attenuation (effective ⊆ delegated ⊆ principal)
- Authorization Decision (ALLOW/DENY/ASK) with reason and provenance
- Integration with Policy/Permission services, Runtime boundary preservation

### Out of scope
- Multi-Tenancy enforcement (TASK-036)
- Distributed runtime (TASK-037)
- Credential isolation (TASK-040)
- Creating a parallel authorization control plane

## Deliverables
- `aios/identity/contracts.py` — Principal, Role, Permission, Policy
- `aios/identity/identity_service.py` — IdentityService (resolve, authorize)
- `aios/identity/rbac.py` — RBAC resolver
- `aios/identity/tests/` — identity, RBAC, ABAC, delegation, fail-closed tests

## Acceptance Criteria
- AC-035-01: Every valid execution has a Principal
- AC-035-02: Principal supports 5 types (User/Service/Agent/Workflow/System)
- AC-035-03: RBAC resolves permissions deterministically
- AC-035-04: ABAC evaluates Subject/Resource/Action/Environment
- AC-035-05: Default deny when required info missing
- AC-035-06: Delegation cannot grant more than principal permissions
- AC-035-07: Agent cannot directly access Identity/Role/Policy storage
- AC-035-08: Authorization decision has reason + provenance
- AC-035-09: INV-022 enforced via architecture test
- AC-035-10: Regression M0–M6 PASS
- AC-035-11: No parallel control plane
- AC-035-12: Evidence retrievable for authorization decisions

## Dependencies
- TASK-034 — Doctor + Readiness

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-022 Identity First enforced.
