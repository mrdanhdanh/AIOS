# Test Matrix — TASK-112

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| plan inference | deterministic, không LLM | test_t112_plan_deterministic |
| dispatch provider enabled | OK | test_t112_dispatch_enabled_ok |
| dispatch provider disabled | reject (T110) | test_t112_dispatch_disabled_rejected |
| provider không hợp lệ | reject (fail-closed) | test_t112_invalid_provider_rejected |
| inference call | provenance đầy đủ (T001) | test_t112_dispatch_enabled_ok |
| cùng plan + state | cùng result (deterministic) | test_t112_plan_deterministic |

6 tests, all passing.
