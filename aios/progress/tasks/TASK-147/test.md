# TASK-147 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| observation rõ | class xác định | PASS |
| observation mơ hồ | UNKNOWN (không promote, T078) | PASS |
| cùng observation | cùng class (deterministic) | PASS |
| thiếu provenance | reject (fail-closed) | PASS |
| taxonomy đóng | label trong tập | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_classification.py` — 7 tests, all passing.
