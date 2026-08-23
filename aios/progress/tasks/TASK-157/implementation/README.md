# TASK-157 — Implementation

## Module
`aios/verification/behavioral.py` — class `BehavioralVerifier`.

## Design
- Immutable dataclasses with `__post_init__` id guards (Rule 1).
- Deterministic method computes a sha256 result id from inputs only.
- Fail-closed: raises `VerificationError` on missing provenance or wrong type.
- Status mapping respects thresholds; UNKNOWN never promoted to PASS (T078).

## Result
Implemented and covered by 7 deterministic tests.
