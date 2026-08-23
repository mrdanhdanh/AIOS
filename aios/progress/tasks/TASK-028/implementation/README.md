# TASK-028 Implementation — Parallel Scheduler

Implementation lives in `aios/parallel_scheduler/` (M5 Core Intelligence — Parallel Scheduler).

```
aios/parallel_scheduler/
  contracts.py  # JoinPolicy (ANY_SUCCESS/ALL_COMPLETED), ScheduledNode, SchedulerState, DispatchDecision
  scheduler.py  # ParallelScheduler (DAG parallel execution within resource/policy boundaries)
  __init__.py   # re-exports
  tests/
    test_scheduler.py
    test_contracts.py
```

Runs DAG in parallel within resource/policy boundaries. Dispatch decisions are explicit (`DispatchDecision` enum).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
