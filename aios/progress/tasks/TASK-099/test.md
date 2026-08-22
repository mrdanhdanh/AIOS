# Test Matrix — TASK-099

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| schedule đến hạn | chạy harness chain | test_schedule_due_runs_harness_chain |
| deviation phát hiện | không PASS, trigger detect (T094) | test_deviation_not_promoted_and_detect_triggered |
| autonomy không allow | không trigger remediation | test_autonomy_not_allowed_no_remediation |
| autonomy allow | trigger remediation (T095-T098) | test_autonomy_allowed_triggers_remediation |
| cùng state + harness | cùng loop result (deterministic) | test_deterministic_loop_result |
| loop evidence | provenance đầy đủ | test_loop_evidence_provenance |

6 tests, all passing.
