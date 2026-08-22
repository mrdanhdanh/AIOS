# TASK-038 — Breakdown

## Steps
1. Create `aios/distributed_scheduler/contracts.py` — Lease (lease_id, node_id, resource_id, state, ttl), LeaseState (HELD/EXPIRED/RELEASED)
2. Create `aios/distributed_scheduler/scheduler.py` — DistributedScheduler: acquire_lease (atomic, single active), release_lease, check_expired, list_leases
3. Implement single active lease enforcement (INV-026): duplicate acquire raises error
4. Implement heartbeat/expiration and failover with fencing
5. Create `aios/distributed_scheduler/tests/` — 5 tests (acquire, duplicate rejected, release, expired, list)
6. Run architecture guard — verify no Scheduler → Resource/Execution implementation ownership
7. Run full suite — 1778/1778 PASS (5 new), no regressions

## Dependencies
- TASK-037 Distributed Runtime

## Exit Criteria
- All AC-038-01..10 PASS, gate PASS, no regressions
