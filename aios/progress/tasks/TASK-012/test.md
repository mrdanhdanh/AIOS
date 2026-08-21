# TASK-012 — Test Report

## Suites

| Suite | File | Cases | Result |
|-------|------|-------|--------|
| goal manager | `aios/orchestrator/tests/test_goal_manager.py` | 19 | PASS |
| task queue | `aios/orchestrator/tests/test_task_queue.py` | 24 | PASS |
| permission broker | `aios/orchestrator/tests/test_permission_broker.py` | 12 | PASS |
| failure recovery | `aios/orchestrator/tests/test_failure_recovery.py` | 18 | PASS |
| orchestration integration | `aios/orchestrator/tests/test_orchestration_integration.py` | 16 | PASS |
| orchestrator (TASK-010) | `aios/orchestrator/tests/test_normalizer.py` etc. | 57 | PASS |
| full harness | `python -m pytest aios -q` | 690 | PASS |

## Coverage

- GoalManager: create/get/list, lifecycle CREATED→PLANNED→ACTIVE→PAUSED→ACTIVE→COMPLETED, pause/resume/cancel, add/remove task, progress, persistence roundtrip (save/load), resume after restart, clear, unknown reject, to_dict.
- TaskQueue: enqueue auto READY, dependency BLOCKED, chain blocked on failure, priority not override dependency, peek priority order, dequeue→RUNNING, pause/resume, cancel, block/unblock (explicit unblock required), prioritize, reorder, duplicate reject, persistence roundtrip, resume, no cron, list_by_status/goal, increment_attempts, clear.
- PermissionBroker: aggregate dedup/normalize, ALLOW when granted+rule, DENY when not granted, ASK when INSUFFICIENT, request/approve (grant on approve), deny, non-ASK reject, empty subject reject, does not decide policy itself (DENY wins), history, clear.
- FailureRecovery: classifier TRANSIENT/RESOURCE/POLICY/VALIDATION/FATAL/LOGICAL, RetryPolicy validate/backoff exponential/fixed, should_retry, bounded retry (max_attempts), no infinite retry, fallback only when policy allows, fallback denied, history, clear, to_dict, policy denied no retry.
- Integration: goal resume after restart, dependency blocked, chain blocked, permission DENY→BLOCKED not dequeueable, retry exhausted, retry success, fallback policy, state authority (execution_id reference), queue separation (no cron), full flow Request→Decision→Goal→Queue→Permission→Recovery.
- `python -m pytest aios -q` — 690 passed, 0 failed.

## AC mapping

| AC | Cases | Result |
|----|-------|--------|
| AC-012-01 goal persistence | test_goal_manager::test_persistence_roundtrip | PASS |
| AC-012-02 resume | test_goal_manager::test_persistence_resume + test_orchestration_integration::TestGoalResume | PASS |
| AC-012-03 dependency | test_task_queue::test_dependency_blocked/chain + test_orchestration_integration::TestTaskDependency | PASS |
| AC-012-04 queue separation | test_task_queue::test_no_cron_scheduling + test_orchestration_integration::TestQueueSeparation | PASS |
| AC-012-05 permission | test_permission_broker (12) + test_orchestration_integration::TestPermissionDeny | PASS |
| AC-012-06 fail closed | test_permission_broker::test_deny_when_not_granted + test_orchestration_integration::TestPermissionDeny | PASS |
| AC-012-07 retry bounded | test_failure_recovery::test_bounded_retry/no_infinite + test_orchestration_integration::TestRetryBounded | PASS |
| AC-012-08 recovery policy | test_failure_recovery::test_fallback_only_when_policy_allows/denied + test_orchestration_integration::TestRecoveryPolicy | PASS |
| AC-012-09 state authority | test_orchestration_integration::TestStateAuthority | PASS |
| AC-012-10 regression | full harness 690 | PASS |
