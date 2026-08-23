# TASK-148 — Implementation

Module: `aios/coding_loop/diagnostic.py`

Exports:
- `DiagnosticAgent` — deterministic diagnostic agent; fail-closed on UNKNOWN.
- `DiagnosticReport` — immutable-by-id diagnostic report (`report_id`, `class_ref`, `observation_ref`, `root_cause`, `confidence`, `evidence_ref`, `authority="aios"`).

Key invariants:
- `diagnose()` fail-closed: requires failure class with `evidence_ref` (T001 Rule 5).
- `report_id` immutable (T001 Rule 1).
- UNKNOWN class → root_cause="UNKNOWN", confidence=0 (never promoted, T078).
- Deterministic: same class → same root cause.
- `provenance()` carries `content_hash` (T078).

Integration: built on Failure Classification T147 + Execution Observation T146 + Evidence T001.
