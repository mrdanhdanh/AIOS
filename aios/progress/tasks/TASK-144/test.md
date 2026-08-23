# TASK-144 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| evidence chuẩn hóa | execution evidence + hash OK | PASS |
| evidence chain | provenance đầy đủ (T001) | PASS |
| evidence không verify | không promote PASS (T078) | PASS |
| evidence_id trùng | REJECT (T001 Rule 1) | PASS |
| cùng evidence + verifier | cùng verdict (deterministic) | PASS |
| evidence bypass policy | bị chặn (T113) | PASS |

Run: `python -m pytest aios/execution/tests/test_evidence.py -q` -> 7 passed.
