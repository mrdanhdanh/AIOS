# TASK-149 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| diagnosis rõ | plan + rollback | PASS |
| plan thiếu rollback | reject (T055) | PASS |
| cùng diagnosis | cùng plan (deterministic) | PASS |
| UNKNOWN diagnosis | reject (T078) | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| thiếu provenance | reject (fail-closed) | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_repair.py` — 7 tests, all passing.
