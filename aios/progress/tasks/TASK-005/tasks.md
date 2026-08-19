# TASK-005 — Breakdown

- [x] **5.1** Fix `aios/core/container.py` — `Lock` -> `RLock` so factories may recursively resolve (deadlock fix for the kernel)
- [x] **5.2** Implement `aios/runtime/execution.py` — Executor, StepResult, ExecutionReport, EventBus events, policy/retry/timeout/cancel/audit
- [x] **5.3** Implement `aios/runtime/scheduler.py` — Scheduler, ScheduledRequest, priority queue + status
- [x] **5.4** Implement `aios/runtime/state.py` — ExecutionState (serializable), StateStore (checkpoint/restore)
- [x] **5.5** Implement `aios/runtime/resource.py` — ResourcePool, ResourceGrant, grant/queue/reject + promotion
- [x] **5.6** Implement `aios/runtime/kernel.py` — RuntimeKernel composing all nine services in a Container
- [x] **5.7** Update `aios/runtime/__init__.py` — export the new TASK-005 public API
- [x] **5.8** Write `test_execution.py` — complete/retry/timeout/cancel/policy/events
- [x] **5.9** Write `test_scheduler.py` — priority/status/cancel/peek
- [x] **5.10** Write `test_state.py` — save/load/serialize/snapshot/delete
- [x] **5.11** Write `test_resource.py` — grant/queue/reject/release-promote/usage
- [x] **5.12** Write `test_kernel.py` — wiring/singletons/executor-through-wiring/external-container/health
- [x] **5.13** Run full test suite — all TASK-001..005 tests green (239 passed)
- [x] **5.14** Write regression.md — verify TASK-001..004 dependency closure green (incl. container RLock)
