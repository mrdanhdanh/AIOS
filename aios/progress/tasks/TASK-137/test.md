# TASK-137 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| tạo workspace | `workspace_id` immutable OK | PASS |
| snapshot state | state_hash + provenance (T001) | PASS |
| restore fail | rollback snapshot (T020/T066) | PASS |
| snapshot không hash được | reject (fail-closed) | PASS |
| cùng state | cùng snapshot (deterministic) | PASS |
| id trùng | REJECT (T001 Rule 1) | PASS |

Run: `python -m pytest aios/execution/tests/test_workspace.py -q` -> 8 passed.
