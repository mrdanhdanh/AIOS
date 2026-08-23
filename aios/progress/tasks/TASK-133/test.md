# Test — TASK-133

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| register + get | version OK | `test_register_and_get` |
| duplicate version | reject (T001 Rule 1) | `test_duplicate_version_rejected` |
| latest version | max version | `test_latest_version` |
| build render | variables OK + hash | `test_build_renders_variables` |
| build deterministic | cùng hash | `test_build_deterministic` |
| missing variable | reject (fail-closed) | `test_build_missing_variable_rejected` |
| unresolved placeholder | reject (T078) | `test_build_unresolved_placeholder_rejected` |
| built prompt evidence | provenance (T001) | `test_built_prompt_has_evidence` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_prompt.py -q
```
Kết quả: 9 passed.
