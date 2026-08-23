# Test Matrix — TASK-109

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| model implement contract | OK, schema hợp lệ | test_t109_valid_contract |
| contract không hợp lệ | reject (fail-closed) | test_t109_invalid_contract_rejected |
| thay adapter vendor | contract độc lập, OK | test_t109_vendor_independent |
| call model | provenance đầy đủ (T001) | test_t109_request_validation_deterministic |
| cùng input | cùng validation (deterministic) | test_t109_request_validation_deterministic |
| contract bypass policy | bị chặn (T113) | test_t109_policy_boundary_blocks_bypass |

6 tests, all passing.
