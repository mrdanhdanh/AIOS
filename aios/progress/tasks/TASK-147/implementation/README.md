# TASK-147 — Implementation

Module: `aios/coding_loop/classification.py`

Exports:
- `FailureClassifier` — deterministic failure classifier with closed taxonomy.
- `FailureClass` — immutable-by-id failure classification (`class_id`, `observation_ref`, `taxonomy_label`, `confidence`, `evidence_ref`, `authority="aios"`).
- `FailureTaxonomy` — SYNTAX / RUNTIME / LOGIC / TIMEOUT / RESOURCE / NETWORK / UNKNOWN (closed).
- `CONFIDENCE_THRESHOLD` = 0.5.

Key invariants:
- `classify()` fail-closed: requires observation with `evidence_ref` (T001 Rule 5).
- `class_id` immutable (T001 Rule 1).
- Confidence < threshold → UNKNOWN (never promoted, T078).
- Deterministic: same observation → same class.
- `provenance()` carries `content_hash` (T078).

Integration: built on Execution Observation T146 + Execution Contract T135 + Evidence T001.
