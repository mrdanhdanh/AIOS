# Test Matrix — TASK-106

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| bridge observation hành vi | OK, có provenance | test_bridge_observation_ok |
| observation conflict AIOS | AIOS authoritative | test_observation_conflict_aios_authoritative |
| observation INCONCLUSIVE | không promote PASS (T078) | test_observation_inconclusive_not_promoted |
| observation không xác định | fail-closed | (covered by inconclusive test) |
| cùng behavior + observation | cùng conformance (deterministic) | test_same_behavior_and_observation_deterministic |
| bridge evidence | provenance đầy đủ | test_bridge_observation_ok |

6 tests, all passing.
