# Test Matrix — TASK-116

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| conformance PASS | certify (T049) | test_t116_conformance_pass_certify |
| conformance FAIL | không certify (fail-closed) | test_t116_conformance_fail_not_certified |
| conformance INCONCLUSIVE | không certify (T078) | test_t116_inconclusive_not_certified |
| cert_id trùng | REJECT (T001 Rule 1) | test_t116_duplicate_cert_id_rejected |
| integrity không verify | không certify (T078) | test_t116_integrity_not_verified |
| cùng provider/model + suite | cùng result (deterministic) | test_t116_deterministic_result |

6 tests, all passing.
