# TASK-167 — Task Breakdown

## Implementation steps
1. Define immutable dataclasses (`TestWeaknessAttacker` input/output) with non-empty id guards.
2. Implement the attack/evaluate method (deterministic, fail-closed).
3. Compute deterministic result id via sha256 of inputs (no clock).
4. Map status: BLOCKED / BREACH / UNKNOWN per invariant; BREACH never promoted.
5. Write 7 deterministic tests covering construction, happy path, fail-closed, breach, blocked, non-type, determinism.
6. Wire export into `aios/adversarial/__init__.py`.

## Status
All steps complete; 7 tests green.
