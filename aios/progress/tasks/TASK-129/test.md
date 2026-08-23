# Test — TASK-129

## Test Matrix (mapping → implementation)

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| review artifact sạch | APPROVE | `test_review_clean_approves` |
| finding block | verdict BLOCK (fail-closed) | `test_review_blocking_finding_blocks` |
| finding warn | REQUEST_CHANGES | `test_review_warn_requests_changes` |
| review bypass policy | reject (T113) | `test_policy_rejected` |
| agent_id rỗng | reject (T001 Rule 1) | `test_agent_id_required` |
| cùng artifact + rules | cùng verdict (deterministic) | `test_deterministic_same_content_same_verdict` |
| finding evidence | provenance đầy đủ (T001) | `test_finding_has_evidence` |
| module không import forbidden | BLOCK (ARCH) | `test_module_has_no_forbidden_imports` |

## Command
```
python -m pytest aios/coder/tests/test_review.py -q
```
Kết quả: 8 passed.
