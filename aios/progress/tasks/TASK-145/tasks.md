# TASK-145 — Task Breakdown

1. Định nghĩa `CodingLoopState` (OBSERVING→...→DONE) + `TRANSITIONS` map đóng.
2. `CodingLoopRecord` (immutable `loop_id`) + `TransitionEvent` (provenance).
3. `CodingLoopStateMachine.transition` fail-closed: yêu cầu artifact (T001 Rule 6) + policy_ref (T113).
4. `next_state` deterministic: cùng state → cùng next state.
5. `provenance()` trả content_hash.
6. Tests (`test_state_machine.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
