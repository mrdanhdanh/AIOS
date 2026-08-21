# TASK-012 — Breakdown

- [x] **12.1** Create `aios/progress/tasks/TASK-012/` scaffold — `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`, `review.md`.
- [x] **12.2** Implement `aios/orchestrator/goal_manager.py` — `Goal`, `GoalStatus`, `GoalManager` with lifecycle, progress, persistence, thread-safe.
- [x] **12.3** Implement `aios/orchestrator/task_queue.py` — `Task`, `TaskStatus`, `TaskPriority`, `TaskQueue` with dependency/priority, logical queue ops, persistence.
- [x] **12.4** Implement `aios/orchestrator/permission_broker.py` — `OrchestratorPermissionBroker` with aggregate, delegate to PolicyEngine, ALLOW/DENY/ASK, human approval.
- [x] **12.5** Implement `aios/orchestrator/failure_recovery.py` — `FailureClassifier`, `RetryPolicy`, `FailureRecovery` with bounded retry, policy-gated fallback, history.
- [x] **12.6** Update `aios/orchestrator/__init__.py` — re-exports for TASK-012.
- [x] **12.7** Create `aios/orchestrator/tests/` — 5 test files covering AC-012-01..10 (≥40 tests) + integration + architecture.
- [x] **12.8** Run `python -m pytest aios -q` — verify 601+ tests PASS, no architecture violations.
- [x] **12.9** Write `test.md` + `evaluation.md` + `REGRESSION.md` with evidence.
- [x] **12.10** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-012 DONE.
