# TASK-005 — Critique 1

## Strengths
- Completes the runtime substrate cleanly: execution, scheduler, state,
  resource, and a composition root. Good separation of concerns.
- Deterministic-first is preserved: the Executor never calls an LLM; policy
  decides before execution; `INSUFFICIENT`/`DENY` are fail-closed.
- Checkpoint/restore via plain serializable state enables real resume.
- Resource pool has clear grant/queue/reject semantics with promotion on
  release.

## Risks / Gaps
1. **Container deadlock**: a DI factory that recursively resolves other
   registered services self-deadlocks because `Container` uses a non-reentrant
   `Lock`. The kernel's Executor factory hits this. Fix: use `RLock`.
2. **Cancel granularity**: cancel is checked only *between* steps; a long
   in-flight step is not interrupted mid-execution. Document this limitation.
3. **Scheduler vs orchestration**: this is the *technical* queue; the logical
   task queue belongs to orchestration (TASK-012). The boundary must stay clear
   to avoid confusion.
4. **Timeout enforcement**: `ThreadPoolExecutor` per step makes timeout
   best-effort (the thread is joined on shutdown). Fine for M1 but note it.

## Required Revisions
- `Container._lock` -> `RLock` (done — resolves kernel deadlock).
- Document cancel-between-steps and timeout best-effort in module docstrings
  (done).
- Scheduler docstring clarifies it is the technical queue, not the logical task
  queue (done).
