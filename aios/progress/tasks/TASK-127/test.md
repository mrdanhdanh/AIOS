# Test — TASK-127

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| execute plan | artifact sinh ra OK | `test_execute_plan_emits_artifacts` |
| artifact hash | content_hash + provenance (T001) | `test_artifact_has_content_hash_and_evidence` |
| plan chưa verify | reject (fail-closed) | `test_unverified_plan_rejected` |
| artifact không hash được | reject (fail-closed, T078) | `test_unhashable_artifact_rejected` |
| cùng plan | cùng artifact set (deterministic) | `test_same_plan_same_artifact_set` |
| agent gọi tool trực tiếp | BLOCK (ARCH-004) | `test_module_has_no_forbidden_imports` |
| runtime dùng capability | không direct tool | `test_runtime_uses_capability_not_direct_tool` |

## Command
```
python -m pytest aios/coder/tests/test_generation.py -q
```
Kết quả: 7 passed.
