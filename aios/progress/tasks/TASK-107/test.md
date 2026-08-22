# Test Matrix — TASK-107

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| bridge permission check | OK, có provenance | test_bridge_permission_check_ok |
| bridge sandbox check | OK, có provenance | test_bridge_sandbox_check_ok |
| independent result conflict AIOS | AIOS authoritative | test_independent_result_conflict_aios_authoritative |
| result INCONCLUSIVE | không promote PASS (T078) | test_result_inconclusive_not_promoted |
| result không xác định | fail-closed | test_result_undefined_fail_closed |
| cùng check + input | cùng policy result (deterministic) | test_same_check_and_input_deterministic |

6 tests, all passing.
