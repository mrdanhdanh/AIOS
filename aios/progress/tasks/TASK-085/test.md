# Test — TASK-085

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| detect 1.0 | plan đúng | PASS |
| verify FAIL | không apply (fail-closed) | PASS |
| bước có down | rollback 1.0 thành công | PASS |
| dry-run | không mutate | PASS |
| migrate state | không mất data (T066) | PASS |
| cùng plan + state | cùng kết quả (deterministic) | PASS |
| non-reversible plan | bị chặn | PASS |
| provenance | evidence ghi đủ | PASS |

`python -m pytest aios/migration -q` → 8 passed.
