# TASK-003 — Critique 2

## Convergence with Critique 1
Both critiques agree on thread safety, event error handling, contract versioning
formula, and step mutability. This second critique adds the following
observations.

## Additional Observations
1. **DI factory functions**: Allow registering a callable (factory) instead of
   a class, so tests can inject mocks without subclassing.
2. **Event bus ordering**: Document that subscribers are called in registration
   order; this is important for deterministic replay in the harness.
3. **Version precedence**: Pre-release versions (`1.0.0-alpha.1`) should sort
   lower than the corresponding release (`1.0.0`). This matters for contract
   compatibility checks.
4. **Execution plan step IDs**: Each step must have a unique ID so that later
   tasks (DAG compiler, scheduler) can reference steps unambiguously.
5. **No external dependencies**: All four modules must be pure-Python with no
   third-party imports beyond the standard library, keeping the offline-first
   principle.

## Required Revisions
- Container `register()` accepts both classes and callables (done).
- Event bus dispatches in registration order; documented (done).
- `SemVer` handles pre-release segments correctly (done).
- `Step` has a required `step_id: str` field (done).
- All modules use only stdlib imports (done).
