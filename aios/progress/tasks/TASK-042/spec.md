# TASK-042 — Enterprise Operations + Dashboard

## Objective
Build Enterprise Operations layer with Control Plane for Health, Metrics, Audit, Runtime/Tenant/Cost/Recovery operations and Dashboard API. Dashboard is projection of true state (not a control plane), with tenant isolation enforced server-side and UNKNOWN never promoted to HEALTHY.

## Scope
### In scope
- Enterprise Operations: Health, Metrics, Audit, Runtime Operations, Tenant Operations, Cost/Resource Operations, Recovery Status, Dashboard API
- Dashboard views: System Overview, Runtime Operations, Tenant Operations, Execution Operations, Audit, Recovery
- Enterprise Observability: Evidence/Event with tenant/project/user/agent/workflow/model/runtime/region dimensions
- Operational API: /operations/health, /overview, /runtimes, /executions, /tenants/{id}, /audit, /recovery, /metrics (all with Identity→Tenant→Policy→Authorization)
- Health model: HEALTHY/DEGRADED/UNHEALTHY/UNKNOWN (UNKNOWN not HEALTHY)
- Metrics: Execution, Resource, AI, Governance, Runtime
- Dashboard security: server-side tenant filtering

### Out of scope
- Creating a parallel control plane
- Replacing Harness or Runtime observability

## Deliverables
- `aios/operations/contracts.py` — Operation, OperationStatus, OperationLog
- `aios/operations/operations_manager.py` — OperationsManager (create, execute, list, logs)
- `aios/operations/tests/` — operations tests

## Acceptance Criteria
- AC-042-01: Enterprise Operations API works
- AC-042-02: Dashboard reads true state from API
- AC-042-03: Runtime health displayed correctly
- AC-042-04: Execution metrics have tenant/project/user dimensions
- AC-042-05: Cost/token/resource metrics retrievable
- AC-042-06: Audit events searchable/filterable
- AC-042-07: Recovery/failover status displayable
- AC-042-08: Tenant A cannot read Tenant B data
- AC-042-09: Dashboard does not bypass Policy/Permission
- AC-042-10: UNKNOWN not promoted to HEALTHY/PASS
- AC-042-11: No parallel control plane
- AC-042-12..19: Unit/Contract/Integration/Architecture/E2E/Regression/Evidence/INV PASS

## Dependencies
- TASK-041 — HA + Audit + Recovery

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-022..029 preserved.
