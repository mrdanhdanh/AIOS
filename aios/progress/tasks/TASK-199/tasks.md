# TASK-199 — Task Breakdown

## Implementation steps
1. Define immutable dataclasses / enums for `PolicyEngine` with non-empty id guards.
2. Implement the validate/assess/evaluate/run method (deterministic, fail-closed).
3. Compute deterministic result id via sha256 of inputs (no clock).
4. Map status: PASS / INSUFFICIENT / UNKNOWN per invariant; UNKNOWN never promoted.
5. Write deterministic tests covering construction, happy path, fail-closed, insufficient/unknown, determinism.
6. Wire export into `aios/coding_edition/__init__.py`.

## Status
All steps complete; tests green for `policy.py`.
