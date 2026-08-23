# Test — TASK-130

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| artifact chuẩn hóa | code/patch/review + hash OK | `test_artifact_standardized_with_hash` |
| artifact evidence chain | provenance đầy đủ (T001) | `test_artifact_evidence_chain` |
| artifact verify OK | VERIFIED (promote) | `test_verify_ok_promotes_verified` |
| artifact thiếu evidence | không promote (fail-closed, T078) | `test_verify_missing_evidence_rejects` |
| artifact bypass policy | reject (T113) | `test_verify_policy_rejected` |
| artifact_id trùng | immutable (T001 Rule 1) | `test_artifact_id_immutable_no_reuse` |
| cùng artifact + verifier | cùng verdict (deterministic) | `test_verify_deterministic` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_artifact.py -q
```
Kết quả: 8 passed.
