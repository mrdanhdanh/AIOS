# Test Matrix — TASK-124

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| harness chạy pipeline | T117->T123 OK, deterministic | test_t124_harness_pipeline_runs |
| stage PASS hết | conformance PASS | test_t124_conformance_pass |
| stage FAIL | conformance FAIL (fail-closed) | test_t124_stage_fail_conformance_fail |
| stage INCONCLUSIVE | conformance FAIL (T078) | test_t124_stage_inconclusive_conformance_fail |
| integrity không verify | conformance FAIL (T078) | test_t124_integrity_not_verified_conformance_fail |
| cùng input + suite | cùng result (deterministic) | test_t124_deterministic |

6 tests, all passing.
