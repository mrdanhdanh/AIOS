# TASK-065 — Critique 1

## Strengths
- Clear hardening scope; explicitly avoids contract changes (T063/T064 frozen).
- Reuses `aios.core.config.Config` and `aios.observability` rather than reinventing.
- Deterministic-first approach aligns with AGENTS.md §6.

## Risks / Gaps
- `observability.py` imports `aios.observability` — must be guarded (import-safe) to avoid breaking runtime when backend is absent.
- `ResourceGuard` reads `ResourcePool._lock`/`_capacity`/`_used` (private attrs) — acceptable within same layer but should be documented as a hardening coupling.
- `Executor` observability must be optional (default `None`) to keep existing tests green.

## Required revisions
- Guard the `aios.observability` import with try/except (done in implementation).
- Keep all new params optional with `None` defaults.
- Add explicit AC table to `evaluation.md`.
