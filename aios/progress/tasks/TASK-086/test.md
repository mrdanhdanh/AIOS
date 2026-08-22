# Test — TASK-086

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| 1.0 consumer gọi 1.x API | works (compat) | PASS |
| break 1.0 schema | BLOCK (phải MAJOR) | PASS |
| compat test PASS | DONE allowed | PASS |
| compat test FAIL | BLOCK (fail-closed) | PASS |
| cùng surface + version | cùng kết quả (deterministic) | PASS |
| compat evidence | provenance đầy đủ | PASS |
| suite hash | deterministic | PASS |

`python -m pytest aios/backward_compat -q` → 7 passed.
