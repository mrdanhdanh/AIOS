# Test — TASK-131

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| conformance PASS | status PASS + security ALLOWED | `test_conformance_pass` |
| hash mismatch | FAIL (fail-closed) | `test_hash_mismatch_fails` |
| thiếu evidence | FAIL (T001) | `test_missing_evidence_fails` |
| integrity chưa verify | FAIL (T078) | `test_integrity_not_verified_fails` |
| producer unauthorized | DENIED + FAIL (T113) | `test_unauthorized_producer_denied` |
| forbidden op | DENIED | `test_forbidden_op_denied` |
| UNKNOWN promote | False (fail-closed, T078) | `test_unknown_never_promoted` |
| result evidence | provenance đầy đủ (T001) | `test_result_has_evidence` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_conformance.py -q
```
Kết quả: 9 passed.
