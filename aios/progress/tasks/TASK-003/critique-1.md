# TASK-003 — Critique 1

## Strengths
- Covers the four foundational primitives (versioning, contracts, DI, events)
  that every later module depends on.
- Ties acceptance criteria to automated tests, consistent with TASK-001/002
  governance principles.
- Execution plan primitives provide a natural extension point for TASK-010
  (Decision Pipeline) without over-engineering now.

## Risks / Gaps
1. **DI thread safety**: The container must be safe to use from multiple threads
   if the runtime ever runs concurrent workflows. The spec does not mention
   locking.
2. **Event bus error handling**: If a subscriber raises, should the bus continue
   dispatching to remaining subscribers or abort? Must be explicit.
3. **Contract versioning**: The spec says "version metadata" but does not define
   the compatibility formula (e.g. semver range `>=1.0.0,<2.0.0`). Need a
   clear rule.
4. **Execution plan immutability**: Should `Step` be mutable (allow status
   updates) or immutable with replacement semantics? Mutable is simpler but
   risks accidental state mutation.

## Required Revisions
- Add a `threading.Lock` to the container for thread-safe resolution (done).
- Event bus continues dispatching on subscriber error; logs warning (done).
- Contracts use semver range with `>=` lower bound and `<` upper bound (done).
- `Step` is mutable with explicit `transition()` method that validates the
  target state (done).
