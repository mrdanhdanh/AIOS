# Test — TASK-132

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| SUPERVISED không apply | denied | `test_supervised_cannot_apply` |
| ASSISTED generate không apply | generate OK, apply denied | `test_assisted_can_generate_not_apply` |
| AUTONOMOUS apply+patch | allowed | `test_autonomous_can_apply_and_patch` |
| require bị deny | raise (fail-closed, T113) | `test_require_raises_on_denial` |
| policy reject | denied | `test_policy_rejected` |
| unknown op | denied | `test_unknown_operation_denied` |
| agent_id rỗng | reject (T001 Rule 1) | `test_agent_id_required` |
| decision evidence | provenance đầy đủ (T001) | `test_decision_has_evidence` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_autonomy.py -q
```
Kết quả: 9 passed.
