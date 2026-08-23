# TASK-180 — Test Report

## Suite
`aios/quality_gate/tests/test_release_gate.py`

## Cases (7, all deterministic)
1. Construction / immutable id guard.
2. Happy path -> expected status.
3. Fail-closed: missing provenance / wrong input raises QualityGateError.
4. Insufficient / boundary case.
5. UNKNOWN / blocked path (never promoted to PASS).
6. Wrong-type input rejected.
7. Deterministic result id (same inputs -> same id).

## Result
7 passed.
