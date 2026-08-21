# TASK-012 Implementation — Operational Orchestration

Implementation lives in `aios/orchestrator/` (M2 Operational Orchestration).

```
aios/orchestrator/
  goal_manager.py        # Goal, GoalStatus, GoalManager
  task_queue.py          # Task, TaskStatus, TaskPriority, TaskQueue
  permission_broker.py   # OrchestratorPermissionBroker
  failure_recovery.py    # FailureClassifier, RetryPolicy, FailureRecovery
  __init__.py            # re-exports (TASK-010 + TASK-012)
  tests/
    test_goal_manager.py
    test_task_queue.py
    test_permission_broker.py
    test_failure_recovery.py
    test_orchestration_integration.py
```

See `../spec.md`, `../test.md`, `../evaluation.md`, `../REGRESSION.md` for
acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (690 PASS).
