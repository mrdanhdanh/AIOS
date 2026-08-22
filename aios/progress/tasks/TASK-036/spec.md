# TASK-036 — Multi-Tenancy + Tenant Boundary

## Objective
Make Tenant a true security boundary enforced across API, Identity, Tenant Context, Policy, Orchestrator, Memory, Registry, Runtime, Storage, Tool, and Audit. Every resource (Execution, Workflow, Agent, Memory, Artifact, Skill, Credential, Evaluation, Harness Run) has tenant ownership. Cross-tenant access denied by default (INV-023).

## Scope
### In scope
- Tenant model: Organization, Tenant, Project, Workspace, TenantContext, TenantResource, TenantScope
- Tenant Context propagation (tenant_id, organization_id, project_id, workspace_id, principal_id)
- Resource ownership matrix for all resource types
- Tenant isolation enforcement at API, Context, Memory, Registry, Runtime, Storage, Tool, Audit
- Memory isolation: tenant-scoped namespace, retrieval, ranking, filtering — no cross-tenant leakage
- Tenant-aware execution flow: Identity → Tenant → Policy → Orchestrator → Memory/Planning → Execution → Artifact/Audit
- Audit with tenant identity and cross-tenant denial evidence
- Fail-closed on UNKNOWN/missing tenant

### Out of scope
- Distributed runtime implementation (TASK-037)
- Credential isolation details (TASK-040)
- Creating a parallel tenant control plane

## Deliverables
- `aios/tenancy/contracts.py` — Tenant, TenantStatus, TenantBoundary
- `aios/tenancy/tenant_manager.py` — TenantManager (create, get, list, enforce boundary)
- `aios/tenancy/tests/` — tenant isolation, cross-tenant negative, memory isolation tests

## Acceptance Criteria
- AC-036-01: Tenant model has clear contract
- AC-036-02: Principal from TASK-035 bound to TenantContext
- AC-036-03: Resource ownership determined
- AC-036-04: Cross-tenant access denied by default
- AC-036-05: Missing/unknown tenant fail-closed
- AC-036-06: Memory retrieval does not leak cross-tenant
- AC-036-07: Artifact/workflow/skill/evaluation/harness isolation enforced
- AC-036-08: Audit records tenant boundary violations
- AC-036-09: Policy remains final authority
- AC-036-10: No parallel control plane
- AC-036-11: INV-023 enforced via automated test
- AC-036-12: Regression M0–M6 PASS
- AC-036-13: Evidence with full provenance
- AC-036-14: Harness verification for positive and negative cases

## Dependencies
- TASK-035 — Identity + Principal + RBAC/ABAC

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-022 Identity First, INV-023 Tenant Isolation enforced.
