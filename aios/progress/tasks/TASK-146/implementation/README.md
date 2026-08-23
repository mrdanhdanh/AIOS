# TASK-146 — Implementation

Module: `aios/coding_loop/observation.py`

Exports:
- `ExecutionObservation` — captures execution traces with provenance; deterministic + fail-closed.
- `Observation` — immutable-by-id execution observation (`observation_id`, `loop_ref`, `execution_ref`, `trace`, `evidence_ref`, `authority="aios"`).
- `ObservationStatus` — CAPTURED / REJECTED.

Key invariants:
- `capture()` fail-closed: requires `execution_ref` + `loop_ref` + `evidence_ref` (T001 Rule 5).
- `observation_id` immutable (T001 Rule 1).
- Deterministic: same execution → same (redacted) trace.
- Secrets redacted via `redact_secret` (T040/T113).
- `provenance()` carries `content_hash` (T078).

Integration: built on Execution Contract T135 + Collector T141 + Evidence T001.
