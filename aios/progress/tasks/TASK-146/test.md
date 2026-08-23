# TASK-146 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| capture trace đủ | observation có provenance | PASS |
| observation thiếu provenance | reject (fail-closed) | PASS |
| cùng execution | cùng trace (deterministic) | PASS |
| thiếu loop link | reject | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| secret redacted | không lộ secret | PASS |
| get unknown | reject | PASS |

**Test file:** `aios/coding_loop/tests/test_observation.py` — 7 tests, all passing.
