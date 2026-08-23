# TASK-150 — Implementation

Module: `aios/coding_loop/progress_detection.py`

Exports:
- `ProgressRegressionDetector` — deterministic progress + regression detector.
- `ProgressReport` — immutable-by-id progress/regression report (`report_id`, `loop_ref`, `plan_ref`, `progress_metric`, `regression_flag`, `evidence_ref`, `authority="aios"`).

Key invariants:
- `detect()` fail-closed: requires `loop_ref` + `plan_ref` + `evidence_ref` (T001 Rule 5).
- `report_id` immutable (T001 Rule 1).
- Regression = `progress_metric < baseline` (T033).
- Deterministic: same state → same verdict.
- `provenance()` carries `content_hash` (T078).

Integration: built on Repair Planner T149 + Benchmark/Regression T033 + Autonomous Recovery T055 + Evidence T001.
