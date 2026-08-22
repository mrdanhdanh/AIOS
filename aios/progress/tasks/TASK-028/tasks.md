# TASK-028 — Breakdown

## Steps
1. Create `aios/parallel_scheduler/contracts.py` — ScheduleRequest, ScheduleDecision, DispatchDecision, SchedulerState contracts
2. Create `aios/parallel_scheduler/scheduler.py` — ParallelScheduler: dependency-aware readiness (PENDING→READY→RUNNING→SUCCEEDED/FAILED), parallel dispatch, resource/policy boundary, JoinPolicy (ALL_SUCCESS/ANY_SUCCESS/ALL_COMPLETED), priority/fairness, backpressure
3. Implement separation: Scheduler → Resource Service (GRANTED/QUEUED/REJECTED) → Execution Service → State Service (INV-016)
4. Create `aios/parallel_scheduler/tests/test_scheduler.py` — 10 tests (readiness, parallel dispatch, resource boundary, policy boundary, failure semantics, join policy, backpressure)
5. Run architecture guard — verify no Scheduler → allocate_gpu/reserve_memory/execute direct calls
6. Run full suite — 1717/1717 PASS (10 new), no regressions

## Dependencies
- TASK-027 Execution Graph

## Exit Criteria
- All AC-028 PASS, gate PASS, no regressions
