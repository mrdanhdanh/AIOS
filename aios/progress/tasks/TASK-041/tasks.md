# TASK-041 — Breakdown

## Steps
1. Create `aios/ha/contracts.py` — HAConfig (primary_node, replica_nodes, health_check_interval, auto_failover), RecoveryPlan (plan_id, steps, auto_failover)
2. Create `aios/ha/ha_manager.py` — HAManager: configure, register_node, health_check, failover (select healthy replica), get_status, create_recovery_plan
3. Implement health state machine and drain protocol
4. Implement lease safety: one active lease, fencing stale leases
5. Implement recovery with evidence chain and audit integration
6. Create `aios/ha/tests/` — 5 tests (configure, register, health, failover, recovery plan)
7. Run architecture guard — verify no new distributed orchestrator, no bypass
8. Run full suite — 1793/1793 PASS (5 new), no regressions

## Dependencies
- TASK-040 Credential + Isolation

## Exit Criteria
- All AC-041-01..12 PASS, gate PASS, no regressions
