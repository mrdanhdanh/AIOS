# TASK-029 — Breakdown

## Steps
1. Create `aios/harness/contracts.py` — HarnessSpec, HarnessRun, RunStatus (8 states), RunResult, Assertion, HarnessError, _VALID_TRANSITIONS map
2. Create `aios/harness/kernel.py` — HarnessKernel: create_run (unique run_id), execute (CREATED→PREPARING→VALIDATING→RUNNING→VERIFYING→COMPLETED), register_step hooks, fail-closed on exception → FAILED, get_run/list_runs
3. Implement lifecycle validation: invalid transition raises HarnessError, FAILED→DIAGNOSED supported
4. Implement thread-safe run registry (threading.Lock)
5. Create `aios/harness/tests/test_kernel.py` — 11 tests (contracts, lifecycle, invalid transition, full lifecycle, step hooks, failure, list_runs)
6. Run architecture guard — verify no Harness → Runtime Service implementation imports
7. Run full suite — 1728/1728 PASS (11 new for kernel), no regressions

## Dependencies
- TASK-028 Parallel Scheduler

## Exit Criteria
- All AC-029-01..10 PASS, gate PASS, no regressions
