# TASK-185 — Task Breakdown

## Implementation steps
1. Define immutable dataclasses (`EvaluationContractValidator` input/output) with non-empty id guards.
2. Implement the validate/score/evaluate/run method (deterministic, fail-closed).
3. Compute deterministic result id via sha256 of inputs (no clock).
4. Map status: PASS / INSUFFICIENT / UNKNOWN per invariant; UNKNOWN never promoted.
5. Write 7 deterministic tests covering construction, happy path, fail-closed, insufficient, unknown, non-type, determinism.
6. Wire export into `aios/evaluation/__init__.py`.

## Status
All steps complete; 7 tests green.
