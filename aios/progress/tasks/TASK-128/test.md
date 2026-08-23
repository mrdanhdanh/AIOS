# Test — TASK-128

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| diff từ artifact | unified diff OK | `test_diff_from_artifact` |
| cùng artifact + target | cùng diff (deterministic) | `test_diff_deterministic` |
| apply có backup | OK | `test_apply_with_backup` |
| apply fail | rollback (T020/T066) | `test_apply_fail_rolls_back` |
| apply bypass policy | reject (T113) | `test_policy_rejected` |
| rollback | certified state | `test_rollback_returns_certified_state` |
| patch hash | content_hash + provenance (T001) | `test_patch_has_hash_and_evidence` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_patch.py -q
```
Kết quả: 8 passed.
