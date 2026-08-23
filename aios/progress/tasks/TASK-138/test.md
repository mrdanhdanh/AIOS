# TASK-138 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| vượt resource limit | BLOCK (T039) | PASS |
| network egress deny | BLOCK (T040) | PASS |
| command không allow | BLOCK | PASS |
| policy vi phạm | fail-closed (T078) | PASS |
| cùng policy + request | cùng decision (deterministic) | PASS |
| policy evidence | provenance đầy đủ (T001) | PASS |

Run: `python -m pytest aios/execution/tests/test_policy.py -q` -> 9 passed.
