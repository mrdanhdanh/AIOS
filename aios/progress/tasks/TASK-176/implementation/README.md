# TASK-176 — Implementation

## Module
`aios/quality_gate/risk_model.py` — class `RiskModel`.

## Design
- Immutable dataclasses with `__post_init__` id guards (Rule 1).
- Deterministic method computes a sha256 result id from inputs only.
- Fail-closed: raises `QualityGateError` on missing provenance or wrong type.
- Status mapping respects invariants; UNKNOWN never promoted to PASS (T078).

## Result
Implemented and covered by 7 deterministic tests.
