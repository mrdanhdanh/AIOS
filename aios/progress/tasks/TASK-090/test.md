# Test Matrix — TASK-090

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| coverage đủ ngưỡng | READY | test_coverage_full_threshold_ready |
| coverage thấp | NOT_READY (fail-closed) | test_coverage_low_not_ready_fail_closed |
| gap tồn tại | report đầy đủ | test_gap_reported_not_hidden |
| cùng system + harness | cùng coverage (deterministic) | test_same_system_same_coverage_deterministic |
| readiness evidence | provenance đầy đủ | test_readiness_evidence_provenance |
| harness chạy certify | sẵn sàng (READY only) | test_harness_certify_ready_only |
| from behavior scenarios | đăng ký surface | test_from_behavior_scenarios_registers_surfaces |

7 tests, all passing.
