# TASK-037 — Distributed Runtime + Runtime Node

## Objective
Separate Runtime Kernel from single-process assumption by creating Runtime Node abstraction and Runtime Router. Router selects nodes based on tenant, region, capability, capacity, health, latency, policy, and cost — without becoming a Kubernetes/cloud orchestrator. Runtime Node contains the existing Runtime Kernel.

## Scope
### In scope
- Runtime Node contract (node_id, version, region, capabilities, capacity, health, tenant_classes, metadata)
- Runtime Node lifecycle: REGISTERED → HEALTHY → DRAINING → UNAVAILABLE → REMOVED (UNKNOWN not healthy)
- RuntimeNodeRegistry: register, unregister, get, list, heartbeat, mark_unhealthy, find_candidates (no execution)
- Runtime Router: candidate selection via NodeCandidateResolver, NodeHealthFilter, CapabilityMatcher, CapacityFilter, NodeSelector
- Tenant/policy-aware selection (tenant context required, UNKNOWN health → not selected)
- Multi-node Runtime integration (Control Plane → Runtime Router → Runtime Nodes → Runtime Kernel)

### Out of scope
- Distributed Scheduler / Lease / Failover (TASK-038)
- Quota/Cost governance (TASK-039)
- Creating a second Runtime Service

## Deliverables
- `aios/distributed/contracts.py` — RuntimeNode, NodeState
- `aios/distributed/node_manager.py` — NodeManager (register, get, list, set_state, get_healthy)
- `aios/distributed/tests/` — distributed runtime tests

## Acceptance Criteria
- AC-037-01: Runtime contract not broken
- AC-037-02: No Policy/Permission bypass
- AC-037-03: No cross-tenant node selection
- AC-037-04: No Scheduler/Lease/Failover in TASK-037 scope
- AC-037-05: Regression M1–M6 PASS
- AC-037-06: Architecture tests PASS
- AC-037-07: Harness simulation proves multi-node routing

## Dependencies
- TASK-036 — Multi-Tenancy + Tenant Boundary

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-022 Identity First, INV-023 Tenant Isolation preserved.
