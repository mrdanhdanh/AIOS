# TASK-065 — Runtime Production Hardening

## Objective
Harden `aios/runtime/` for production: fail-closed config validation, bounded
retry with backoff + escalation, observability traces on every failure path,
resource-limit guards, and a `RuntimeHealth` model. This is **hardening**, not a
new feature — no layer/public contract changes (frozen at T063/T064).

## Scope
**In scope**
- `aios/runtime/config_guard.py` — fail-closed config validation (`ConfigValidationError`).
- `aios/runtime/retry.py` — bounded retry + backoff + escalate callback (no infinite loop).
- `aios/runtime/observability.py` — JSON log + metrics facade; every failure path emits a trace.
- `aios/runtime/resource.py` — `ResourceGuard` guarding exhaustion, degrading safe.
- `aios/runtime/health.py` — `RuntimeHealth` dataclass + `HealthMonitor`.
- Integration: `Executor` gains optional `observability` hook; `RuntimeKernel` refuses invalid config.

**Out of scope**
- New public/runtime contracts (frozen T063/T064).
- Durable execution (T066).

## Deliverables
- 5 new/extended runtime modules (above).
- 9 governance artifacts under `aios/progress/tasks/TASK-065/`.
- Tests under `aios/runtime/tests/` passing `python -m pytest aios/runtime -q`.

## Acceptance Criteria
- AC1: Invalid config → refuse start (fail-closed, typed error).
- AC2: Retry bounded; exceeding limit → escalate (no infinite loop).
- AC3: Every failure path emits an observability trace.
- AC4: Resource exhaustion guarded + degrade safe.
- AC5: Hardening does not break layer contract (T063) / public contract (T064).
- AC6: Same error input + same policy → same behaviour (deterministic).
- AC7: Regression of prior milestones PASS; no invariant violations.

## Dependencies
- TASK-064 (Public Contract Freeze) — completed.

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`; architecture guard (ARCH-001..004) respected.
