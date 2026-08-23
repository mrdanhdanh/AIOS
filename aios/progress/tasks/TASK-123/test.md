# Test Matrix — TASK-123

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| verify context đúng | PASS | test_t123_verify_correct_pass |
| verify context sai | FAIL (fail-closed) | test_t123_verify_wrong_fail |
| verify INCONCLUSIVE | không promote PASS (T078) | test_t123_inconclusive_not_promoted |
| verification evidence | provenance đầy đủ (T001) | test_t123_evidence_provenance |
| cùng context | cùng result (deterministic) | test_t123_deterministic |
| verify secret | không lộ (T040) | test_t123_secret_not_verified |

6 tests, all passing.
