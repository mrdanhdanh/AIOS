# TASK-171 — Implementation

## Module
`aios/adversarial/execution_integrity_attackers.py` — class `ExecutionIntegrityAttacker`.

## Design
- Immutable dataclasses with `__post_init__` id guards (Rule 1).
- Deterministic method computes a sha256 result id from inputs only.
- Fail-closed: raises `AdversarialError` on missing provenance or wrong type.
- Status mapping respects invariants; BREACH/UNKNOWN never promoted to PASS (T078).

## Result
Implemented and covered by 7 deterministic tests.
