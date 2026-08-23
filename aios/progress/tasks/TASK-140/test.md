# TASK-140 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| chạy build trong sandbox | OK, result có hash | PASS |
| chạy lint trong sandbox | OK, result có hash | PASS |
| policy vi phạm | BLOCK (fail-closed) | PASS |
| chạy ngoài sandbox | bị chặn (T136/T040) | PASS |
| cùng target + env | cùng result (deterministic) | PASS |
| build/lint evidence | provenance đầy đủ (T001) | PASS |

Run: `python -m pytest aios/execution/tests/test_build_lint.py -q` -> 6 passed.
