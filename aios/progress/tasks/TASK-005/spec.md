# TASK-005 — Runtime Services II

## Objective
Complete the runtime control substrate begun in TASK-004 by adding the
execution, scheduling, state, and resource services, and a `RuntimeKernel`
that composes all nine services (TASK-004's five + these four) through the
TASK-003 DI `Container`. Together these let a workflow be executed,
checkpointed, resumed, prioritized, and resource-bounded — entirely through the
runtime, with the policy engine deciding before anything runs.

## Scope
- **Execution** (`aios.runtime.execution`): run an `ExecutionPlan` step-by-step
  with policy pre-check, retry, timeout, cancel, and audit; deterministic-first
  (no LLM).
- **Scheduler** (`aios.runtime.scheduler`): thread-safe priority queue of
  execution requests (the *technical* scheduler, distinct from the logical task
  queue owned by orchestration later).
- **State** (`aios.runtime.state`): serializable `ExecutionState` checkpoints
  for snapshot / resume.
- **Resource** (`aios.runtime.resource`): finite-capacity `ResourcePool` with
  grant / queue / reject semantics, optional policy authorization.
- **RuntimeKernel** (`aios.runtime.kernel`): composes all services in a
  `Container`; exposes typed accessors; provides a health snapshot.

## Deliverables
- `aios/runtime/execution.py` — Executor + report types + EventBus events.
- `aios/runtime/scheduler.py` — Scheduler + ScheduledRequest.
- `aios/runtime/state.py` — ExecutionState + StateStore.
- `aios/runtime/resource.py` — ResourcePool + ResourceGrant.
- `aios/runtime/kernel.py` — RuntimeKernel composition root.
- `aios/runtime/__init__.py` — extended public API.
- `aios/core/container.py` — **hardening**: lock changed to `RLock` so factories
  may recursively resolve services (was a self-deadlock; required by the kernel).
- `aios/runtime/tests/test_execution.py`, `test_scheduler.py`, `test_state.py`,
  `test_resource.py`, `test_kernel.py`.
- `aios/progress/tasks/TASK-005/` governance artifacts.

## Acceptance Criteria
1. **Execute + snapshot/resume**: a plan executes to completion; step statuses
   checkpoint and can be reloaded (automated test PASS).
2. **Retry**: a flaky step succeeds after retries; exhausted retries -> FAILED
   (automated test PASS).
3. **Timeout**: a slow step is marked `TIMEOUT` within budget (automated test PASS).
4. **Cancel**: a set cancel event stops execution between steps (`CANCELLED`)
   (automated test PASS).
5. **Policy pre-check**: a step lacking permission is blocked fail-closed before
   execution (automated test PASS).
6. **Scheduler**: priority ordering + status tracking + cancel-skip (automated
   test PASS).
7. **Resource grant/queue/reject**: capacity enforced; release promotes a
   waiting request (automated test PASS).
8. **Kernel composition**: all nine services resolve from one `Container`; the
   executor runs through the wiring (automated test PASS).
9. **Test suite**: `python -m pytest aios -q` passes with zero failures.
10. **Regression**: TASK-001/002/003/004 tests continue to pass, including the
    `Container` RLock hardening (regression gate).

## Dependencies
- TASK-004 (Runtime Services I) — DONE. Uses ContextStore, AuditTrail,
  ArtifactStore, PermissionBroker, PolicyEngine.
- TASK-003 (Kernel Foundations) — DONE. Uses `ExecutionPlan`/`Step`,
  `EventBus`/`Event`, `Container`.

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: relative imports within
  `aios/runtime/`; no agent/orchestrator imports.
