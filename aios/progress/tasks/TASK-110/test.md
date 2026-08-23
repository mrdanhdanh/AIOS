# Test Matrix — TASK-110

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| đăng ký provider | provider_id immutable OK | test_t110_register_immutable_id |
| đăng ký id trùng | REJECT (T001 Rule 1) | test_t110_duplicate_id_rejected |
| provider unhealthy | không chọn (T025) | test_t110_unhealthy_not_selected |
| provider không hợp lệ | reject (fail-closed) | test_t110_invalid_contract_rejected |
| lifecycle event | provenance đầy đủ (T001) | test_t110_lifecycle_event_provenance |
| thay provider | contract độc lập, OK | test_t110_deprecate_immutable |

6 tests, all passing.
