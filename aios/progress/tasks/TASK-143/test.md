# TASK-143 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| secure run trong sandbox | OK, policy enforced | PASS |
| replay từ evidence | cùng output (deterministic) | PASS |
| replay không khớp | phát hiện (fail-closed) | PASS |
| chạy ngoài sandbox | bị chặn (T136/T040) | PASS |
| replay evidence | provenance đầy đủ (T001) | PASS |
| replay policy vi phạm | BLOCK (T138) | PASS |

Run: `python -m pytest aios/execution/tests/test_replay.py -q` -> 6 passed.
