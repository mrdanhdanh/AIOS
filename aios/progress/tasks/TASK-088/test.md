# Test — TASK-088

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| docs cover T084-T087 | PASS | PASS |
| ADR thiếu rationale | bị chặn | PASS |
| doc stale vs impl | bị chặn | PASS |
| doc link task | provenance đầy đủ | PASS |
| cùng nội dung | cùng review (deterministic) | PASS |
| doc reference valid | không 404 | PASS |
| missing coverage | bị chặn | PASS |

`python -m pytest aios/compat_docs -q` → 7 passed.
