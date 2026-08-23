# TASK-151 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| verify output đúng | PASS | PASS |
| verify output sai | FAIL (fail-closed) | PASS |
| verify INCONCLUSIVE | không promote PASS (T078) | PASS |
| thiếu provenance | reject (fail-closed) | PASS |
| cùng output | cùng result (deterministic) | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_verification_gate.py` — 7 tests, all passing.
