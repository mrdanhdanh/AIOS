# TASK-145 — Test Matrix

| Scenario | Expected | Result |
| -------- | -------- | ------ |
| transition đủ artifact | next state | PASS |
| transition thiếu artifact | reject (fail-closed) | PASS |
| cùng state + input | cùng next state (deterministic) | PASS |
| immutable loop_id | loop_id giữ nguyên | PASS |
| transition thiếu policy | reject (T113) | PASS |
| transition history ghi đủ | len(history)=2 | PASS |
| provenance hash | content_hash present | PASS |

**Test file:** `aios/coding_loop/tests/test_state_machine.py` — 7 tests, all passing.
