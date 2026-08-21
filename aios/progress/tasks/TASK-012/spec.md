# TASK-012 — Operational Orchestration

## Objective
Xây lớp Operational Orchestration nằm giữa Decision Pipeline (TASK-010) và Runtime Kernel (M1). Quản lý goal dài hạn qua nhiều phiên, queue logic tách biệt Scheduler kỹ thuật, broker permission qua Policy/Permission Service, và recovery có giới hạn với evidence — không trở thành Runtime thứ hai.

## Scope
- **Goal Manager** (`aios/orchestrator/goal_manager.py`): Goal contract (id/title/description/status/tasks/created_at/updated_at/metadata/priority), lifecycle CREATED→PLANNED→ACTIVE→PAUSED→ACTIVE→COMPLETED (terminal COMPLETED/FAILED/CANCELLED), progress = completed/total, pause/resume/cancel/retry, persistence (to_dict/from_dict + file), thread-safe RLock, fail-closed.
- **Task Queue** (`aios/orchestrator/task_queue.py`): logical queue (không cron/technical scheduling), Task contract (id/goal_id/status/priority/dependencies/workflow_id/execution_id/attempts), statuses PENDING/READY/RUNNING/PAUSED/BLOCKED/SUCCEEDED/FAILED/CANCELLED, priorities CRITICAL/HIGH/NORMAL/LOW, ops enqueue/dequeue/peek/pause/resume/reorder/prioritize/cancel/block/unblock, dependency-aware (BLOCKED nếu dependency != SUCCEEDED), priority không override dependency, persistence.
- **Permission Broker** (`aios/orchestrator/permission_broker.py`): aggregate permissions (collect/normalize/deduplicate), chuyển sang runtime PermissionBroker/PolicyEngine, trả ALLOW/DENY/ASK, DENY→BLOCKED không tự thử tool khác, ASK→human approval với evidence, không tự quyết policy.
- **Failure Recovery** (`aios/orchestrator/failure_recovery.py`): classifier (TRANSIENT/RESOURCE/POLICY/VALIDATION/LOGICAL/FATAL), retry bounded (max_attempts, exponential backoff), strategies RETRY_SAME/RETRY_WITH_MODIFIED_INPUT/FALLBACK_AGENT/FALLBACK_WORKFLOW/PAUSE_FOR_HUMAN/FAIL, fallback chỉ khi policy cho phép, history, không duplicate Runtime retry engine.
- **Out of scope**: Worker Plane (TASK-013), Tool Router (TASK-014), multi-tenant (M7), cron/scheduler kỹ thuật.

## Deliverables
- `aios/orchestrator/goal_manager.py` — Goal, GoalStatus, GoalManager.
- `aios/orchestrator/task_queue.py` — Task, TaskStatus, TaskPriority, TaskQueue.
- `aios/orchestrator/permission_broker.py` — OrchestratorPermissionBroker, PermissionDecision.
- `aios/orchestrator/failure_recovery.py` — FailureClassifier, RetryPolicy, FailureRecovery, RecoveryStrategy.
- `aios/orchestrator/__init__.py` — re-exports.
- Tests: `aios/orchestrator/tests/test_goal_manager.py`, `test_task_queue.py`, `test_permission_broker.py`, `test_failure_recovery.py`, `test_orchestration_integration.py`, `test_architecture.py` (extended).
- Governance artifacts: `aios/progress/tasks/TASK-012/{spec,critique-1,critique-2,tasks,review,test,evaluation,REGRESSION}.md`.

## Acceptance Criteria
1. **AC-012-01 — Goal persistence**: restart không mất Goal state (to_dict/from_dict + file roundtrip).
2. **AC-012-02 — Resume**: Goal ACTIVE/PAUSED resume đúng task state.
3. **AC-012-03 — Dependency**: Task không READY nếu dependency chưa SUCCEEDED.
4. **AC-012-04 — Queue separation**: TaskQueue không thực hiện cron/technical scheduling (chỉ logical).
5. **AC-012-05 — Permission**: request đi qua Permission/Policy Service (delegate, không tự quyết).
6. **AC-012-06 — Fail closed**: DENY → task không execute (BLOCKED).
7. **AC-012-07 — Retry bounded**: không infinite retry (max_attempts).
8. **AC-012-08 — Recovery policy**: fallback chỉ khi policy cho phép.
9. **AC-012-09 — State authority**: orchestration state không thay thế Runtime execution state (chỉ tham chiếu execution_id).
10. **AC-012-10 — Regression**: `python -m pytest aios -q` xanh, M1 + TASK-010 PASS.

## Dependencies
- TASK-010 Decision Pipeline (DONE), M1 Runtime (TASK-003..011 DONE) — Policy/Permission, State, Scheduler, Execution, Event/Audit.

## Governance references
- Rule 3 Architecture Guard (orchestrator→runtime/capability/tool/unknown), Rule 4 Deterministic-first, Rule 5 Evidence, Rule 7 Regression.
