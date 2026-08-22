# TASK-041 — HA + Audit + Recovery

## Objective
Build production-resilient HA with Runtime health monitoring, drain/lease handling, failover, snapshot/checkpoint resume, and enterprise audit. Ensures no single Runtime Node is SPOF, execution state survives node failure, stale leases are fenced, recovery is evidence-backed, and audit answers Who/What/When/Tenant/Agent/Workflow/Tool/Credential/Policy/Result with immutable tamper-evident trail.

## Scope
### In scope
- HA Runtime pool: heartbeat, health status, registration, drain, unhealthy detection, reassignment, lease expiration, resume from checkpoint, graceful shutdown
- Health state machine: UNKNOWN → HEALTHY → DEGRADED → UNHEALTHY → DRAINING → DRAINED
- Execution Lease Safety: one active lease per execution (INV-026), fencing stale leases
- Recovery: transient retry, drain+failover, lease expired → new lease, checkpoint resume, corrupt snapshot → fail-closed, duplicate block
- Enterprise Audit: structured event (event_id, principal, tenant, execution, workflow, agent, action, resource, capability, tool, credential_scope, policy_decision, result, evidence_ref, correlation_id, integrity_hash), immutable store, evidence linkage
- Recovery evidence chain: Failure → Health → Lease → Checkpoint → Failover → Resume → Verdict
- Harness verification of failure/recovery paths

### Out of scope
- Building a new distributed orchestrator (Control Plane remains authority)
- Enterprise Operations Dashboard (TASK-042)
- Creating a parallel control plane

## Deliverables
- `aios/ha/contracts.py` — HAConfig, RecoveryPlan
- `aios/ha/ha_manager.py` — HAManager (configure, register_node, health_check, failover, get_status, create_recovery_plan)
- `aios/ha/tests/` — HA and recovery tests

## Acceptance Criteria
- AC-041-01: 3 Runtime Nodes in test env, one failure does not lose Control Plane coordination
- AC-041-02: Execution can failover from failed node to healthy node via lease + checkpoint
- AC-041-03: No test allows same execution with two active leases
- AC-041-04: Resume only succeeds with valid snapshot/checksum/provenance
- AC-041-05: Stale lease owner denied from continuing execution
- AC-041-06: Graceful drain supported
- AC-041-07: Audit event has full provenance (Who/What/When/Tenant/Agent/Workflow/Tool/Credential/Policy/Result)
- AC-041-08: Audit immutable / tamper-evident
- AC-041-09: Recovery creates evidence chain
- AC-041-10: UNKNOWN not promoted to RECOVERED
- AC-041-11: No Policy/Permission/Runtime contract bypass
- AC-041-12: Regression M0–M7 PASS

## Dependencies
- TASK-040 — Credential + Network + Sandbox Isolation

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-026 Distributed Execution Safety enforced.
