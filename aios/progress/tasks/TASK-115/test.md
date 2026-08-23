# Test Matrix — TASK-115

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| inference call | sinh UsageRecord + AuditEntry | test_t115_record_and_audit |
| audit entry sửa | phát hiện tamper (T078) | test_t115_tamper_detected |
| usage thiếu hash | reject (fail-closed) | test_t115_missing_hash_rejected |
| cost compute | theo quota (T039) | test_t115_cost_deterministic |
| cùng call | cùng usage/cost (deterministic) | test_t115_cost_deterministic |
| usage evidence | provenance đầy đủ (T001) | test_t115_evidence_provenance |

6 tests, all passing.
