# TASK-005 — Critique 2

## Convergence with Critique 1
Both critiques converge on the container deadlock fix and the cancel/timeout
granularity documentation. This critique adds integration-readiness checks for
the downstream M1 tasks.

## Additional Observations
1. **Kernel as composition root**: `RuntimeKernel` is the right place to wire
   services; later tasks (TASK-006 providers, TASK-007 memory, TASK-008
   workflow, TASK-009 capability) should register into the same `Container` so
   the orchestrator resolves them by type without coupling.
2. **EventBus integration**: the Executor already publishes
   `ExecutionStarted` / `ExecutionStepFinished` on a wired bus — useful for the
   harness replay guarantee.
3. **State persistence**: `ExecutionState.to_dict/from_dict` is JSON-serializable;
   a later task can persist checkpoints as `Artifact`s (ties to TASK-004).
4. **No external deps**: all four new modules + kernel remain pure-Python +
   `aios.core` (confirmed).

## Required Revisions
- Kernel exposes `health()` for a quick wired-services snapshot (done).
- State serialization kept JSON-friendly (done).
- Service constructors remain DI-friendly (done).
