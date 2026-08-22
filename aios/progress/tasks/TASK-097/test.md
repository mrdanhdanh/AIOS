# Test Matrix — TASK-097

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| có permission + low-risk | apply + re-test | test_apply_with_permission_low_risk |
| thiếu permission | không apply (fail-closed) | test_missing_permission_no_apply |
| high-risk không approve | không apply | test_high_risk_no_approval_no_apply |
| re-test FAIL | rollback (T074/T066) | test_re_test_fail_rollback |
| high-risk có approve | certify (T073) | test_high_risk_with_approval_certified |
| cùng candidate + policy | cùng result (deterministic) | test_deterministic_apply_result |

6 tests, all passing.
