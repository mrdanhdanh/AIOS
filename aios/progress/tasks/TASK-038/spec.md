# TASK-038 — Distributed Scheduler + Lease + Failover

## Objective
Build the Distributed Scheduler that ensures execution safety across multiple Runtime Nodes via ExecutionLease (acquire/renew/release/expire), heartbeat, stale detection, failover, and resume from snapshot. Enforces INV-026: one execution has exactly one active lease at a time, with fencing to prevent stale node writes.

## Scope
### In scope
- DistributedScheduler: candidate selection, lease acquisition, dispatch
- ExecutionLease: lease_id, execution_id, node_id, epoch, acquired_at, expires_at, heartbeat_at, status (PENDING→ACQUIRING→ACTIVE→RENEWED/RELEASED/EXPIRED→RESCHEDULE)
- Lease lifecycle: acquire (atomic), renew (heartbeat), release (on completion), expire (on timeout)
- Heartbeat protocol and stale execution detection (NODE_UNHEALTHY, LEASE_EXPIRED, EXECUTION_STALE, etc.)
- Failover flow: detect failure → expire lease → fence old lease → mark stale → find replacement → load snapshot → resume
- Race protection: single active lease, stale completion rejection, fencing via epoch
- Failure policy: max_reschedule, resume_from_snapshot, backoff
- Evidence/audit for lease lifecycle

### Out of scope
- Tenant quota (TASK-039)
- Credential isolation (TASK-040)
- HA infrastructure (TASK-041)
- Building Kubernetes/distributed database

## Deliverables
- `aios/distributed_scheduler/contracts.py` — Lease, LeaseState
- `aios/distributed_scheduler/scheduler.py` — DistributedScheduler (acquire_lease, release_lease, check_expired, list_leases)
- `aios/distributed_scheduler/tests/` — distributed scheduler tests

## Acceptance Criteria
- AC-038-01: Distributed Scheduler works via contract
- AC-038-02: Execution has clear lease
- AC-038-03: Lease acquire/release/renew/expire deterministic
- AC-038-04: Heartbeat and stale detection work
- AC-038-05: No two active leases for same execution
- AC-038-06: Fencing prevents stale node writes
- AC-038-07: Node failure leads to failover per policy
- AC-038-08: Execution with snapshot can resume on another node
- AC-038-09: Retry/reschedule has limits
- AC-038-10: Regression M1–M6 PASS

## Dependencies
- TASK-037 — Distributed Runtime + Runtime Node

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-026 Distributed Execution Safety enforced.
