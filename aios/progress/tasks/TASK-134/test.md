# Test — TASK-134

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| in-scope path | ALLOWED | `test_in_scope_allowed` |
| nested in-scope | ALLOWED | `test_nested_in_scope_allowed` |
| traversal | DENIED (fail-closed) | `test_traversal_denied` |
| absolute outside | DENIED | `test_absolute_outside_denied` |
| require deny | raise (T113) | `test_require_raises_on_denial` |
| missing root | reject | `test_missing_root_rejected` |
| decision evidence | provenance (T001) | `test_decision_has_evidence` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_filesafety.py -q
```
Kết quả: 8 passed.
