# TASK-150 — Task Breakdown

1. Định nghĩa `ProgressReport` (immutable `report_id`, `loop_ref`, `plan_ref`, `progress_metric`, `regression_flag`, `evidence_ref`).
2. `ProgressRegressionDetector.detect` fail-closed: yêu cầu `loop_ref` + `plan_ref` + `evidence_ref`.
3. Regression = `progress_metric < baseline` (T033).
4. Deterministic verdict (cùng state → cùng flag).
5. `provenance()` (content_hash).
6. Tests (`test_progress_detection.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
