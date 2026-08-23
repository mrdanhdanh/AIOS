# TASK-150 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| loop tiến bộ | progress tăng | PASS |
| regression vs baseline | regression_flag=true | PASS |
| cùng state | cùng verdict (deterministic) | PASS |
| thiếu provenance | reject (fail-closed) | PASS |
| thiếu loop link | reject | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_progress_detection.py` — 7 tests, all passing.
