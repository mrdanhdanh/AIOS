# TASK-173 — Boundary Attackers

## Objective
Probe whether boundary escapes are prevented. Deterministic, fail-closed: an escape attempt that is not contained is BREACH; contained attempt or no attempt is BLOCKED.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/boundary_attackers.py` — class `BoundaryAttacker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- BoundaryAttack/BoundaryResult immutable with non-empty attack_id (Rule 1).
- attack: breached = escape_attempt AND not contained; BREACH when breached else BLOCKED.
- Empty attack_id or non-attack input raises AdversarialError (fail-closed).
- BREACH never promoted to PASS (T078).
- result_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
