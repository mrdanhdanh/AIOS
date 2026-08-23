# TASK-153 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| trong boundary | continue | PASS |
| vi phạm boundary | kill switch (T068) | PASS |
| cùng state | cùng decision (deterministic) | PASS |
| thiếu provenance | reject (fail-closed) | PASS |
| duplicate id | reject (T001 Rule 1) | PASS |
| guardrail áp dụng | guardrail_ref đúng | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_safety.py` — 7 tests, all passing.
