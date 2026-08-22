# Test Matrix — TASK-094

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| anomaly xuất hiện | detect được | test_detect_anomaly_oscillation |
| không anomaly | detect None | test_detect_no_anomaly |
| triệu chứng | capture có evidence | test_capture_symptom_with_evidence |
| root cause trace | causal chain đầy đủ | test_root_cause_traceable |
| thiếu evidence | escalate (fail-closed) | test_missing_evidence_escalates |
| thiếu causal trace | escalate | test_missing_causal_trace_escalates |
| cùng incident + evidence | cùng diagnosis (deterministic) | test_deterministic_diagnosis |
| diagnosis report | provenance đầy đủ | test_provenance_complete / test_diagnosis_report_provenance |

9 tests, all passing.
