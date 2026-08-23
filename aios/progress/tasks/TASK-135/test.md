# TASK-135 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| execution implement contract | OK, schema hợp lệ | PASS |
| contract không hợp lệ | reject (fail-closed) | PASS |
| execution call | provenance đầy đủ (T001) | PASS |
| cùng input | cùng validation (deterministic) | PASS |
| contract bypass policy | bị chặn (T113) | PASS |
| contract ref sandbox | link T136 OK | PASS |

Run: `python -m pytest aios/execution/tests/test_contract.py -q` -> 8 passed.
