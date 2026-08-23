# Test — TASK-126

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| plan theo rule | LLM call = 0, deterministic | `test_plan_by_rule_llm_call_zero` |
| rule không đủ | LLM fallback + validator | `test_rule_insufficient_llm_fallback_called` |
| cùng request + rule | cùng plan (deterministic) | `test_deterministic_same_request_same_plan` |
| plan verify OK | verified | `test_verifier_accepts_valid_plan` |
| plan rỗng | reject (fail-closed) | `test_verifier_rejects_empty_plan` |
| plan bypass policy | reject (T113) | `test_verifier_rejects_policy` |
| target không hợp lệ | reject | `test_verifier_rejects_bad_target` |
| plan evidence | provenance đầy đủ (T001) | `test_plan_has_provenance` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_planner.py -q
```
Kết quả: 9 passed.
