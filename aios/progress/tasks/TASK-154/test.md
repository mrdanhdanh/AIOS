# TASK-154 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| chạy loop end-to-end | PASS (T145→T153) | PASS |
| loop fail (UNKNOWN) | harness FAIL (fail-closed, T078) | PASS |
| loop fail (regression) | harness FAIL | PASS |
| immutable run_id | run_id giữ nguyên | PASS |
| provenance | evidence_ref present | PASS |
| cùng input | cùng output (deterministic, T029) | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_harness.py` — 7 tests, all passing.
