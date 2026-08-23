# TASK-139 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| chạy test trong sandbox | OK, result có hash | PASS |
| policy vi phạm | BLOCK (fail-closed) | PASS |
| chạy ngoài sandbox | bị chặn (T136/T040) | PASS |
| test result | content_hash + provenance (T001) | PASS |
| cùng suite + env | cùng result (deterministic) | PASS |
| test evidence | provenance đầy đủ (T001) | PASS |

Run: `python -m pytest aios/execution/tests/test_test_runner.py -q` -> 6 passed.
