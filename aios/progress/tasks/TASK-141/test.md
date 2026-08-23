# TASK-141 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| capture output | stdout/stderr + hash OK | PASS |
| collect artifact | từ T139/T140 OK | PASS |
| output không hash được | reject (fail-closed) | PASS |
| collect secret | không lộ (T040) | PASS |
| cùng run | cùng collected set (deterministic) | PASS |
| collect evidence | provenance đầy đủ (T001) | PASS |

Run: `python -m pytest aios/execution/tests/test_collector.py -q` -> 7 passed.
