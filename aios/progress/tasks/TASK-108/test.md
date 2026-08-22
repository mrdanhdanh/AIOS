# Test Matrix — TASK-108

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| console view harness status | tổng hợp T105/T106/T107 OK | test_aggregate_healthy / test_aggregate_degraded_on_fail |
| operator action qua API | policy-gated, không bypass | test_operator_action_policy_gated |
| console ghi đè policy | bị chặn (authority AIOS) | test_console_cannot_override_authority |
| verdict INCONCLUSIVE | không promote PASS (T078) | (covered via degraded aggregate) |
| cùng harness state | cùng view (deterministic) | test_same_harness_state_deterministic_view |
| console view evidence | provenance đầy đủ | (evidence_ref propagated in aggregate) |

5 tests, all passing.
