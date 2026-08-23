# TASK-148 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| input rõ | root cause xác định | PASS |
| input mơ hồ | UNKNOWN (không promote, T078) | PASS |
| cùng input | cùng root cause (deterministic) | PASS |
| thiếu provenance | reject (fail-closed) | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| root cause mapping | đúng taxonomy | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_diagnostic.py` — 7 tests, all passing.
