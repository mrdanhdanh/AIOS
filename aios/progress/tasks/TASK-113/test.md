# Test Matrix — TASK-113

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| inference qua permission | OK, policy allow | test_t113_permission_allow |
| thiếu permission | BLOCK (fail-closed) | test_t113_missing_permission_blocked |
| credential trong log | bị chặn (T040) | test_t113_credential_not_leaked |
| policy deny | BLOCK (T078) | test_t113_policy_deny_blocked |
| cùng context + policy | cùng decision (deterministic) | test_t113_deterministic_decision |
| security decision | provenance, không có secret | test_t113_credential_not_leaked |

6 tests, all passing.
