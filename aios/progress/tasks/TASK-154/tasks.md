# TASK-154 — Task Breakdown

1. Định nghĩa `CodingHarnessRun` (immutable `run_id`, `loop_ref`, `safety_ref`, `test_ref`, `eval_ref`, `evidence_ref`, `status`) + `HarnessStatus`.
2. `AutonomousCodingHarness.run` điều phối T145→T153 end-to-end, fail-closed (bất kỳ break → FAIL, T078).
3. Duplicate `run_id` → reject (T001 Rule 1).
4. Deterministic run (cùng input → cùng output, T029).
5. `provenance()` (content_hash).
6. Tests (`test_harness.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
