# TASK-152 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| refresh context | context mới (T024) | PASS |
| snapshot mismatch | reject (fail-closed, T137) | PASS |
| cùng state | cùng context (deterministic) | PASS |
| verified output | chain OK | PASS |
| unverified output | reject (T078) | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_patch_chain.py` — 7 tests, all passing.
