# Test Matrix — TASK-091

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| known-answer đúng | meta PASS | test_known_answer_correct_meta_pass |
| harness verdict sai | meta FAIL (fail-closed) | test_harness_wrong_verdict_meta_fail |
| mutation bị phát hiện | meta PASS | test_mutation_detected_meta_pass |
| mutation không bị phát hiện | meta FAIL | test_mutation_undetected_meta_fail |
| verifier không lock | bị chặn (T078) | test_verifier_not_locked_blocked |
| cùng meta-input + harness | cùng result (deterministic) | test_same_meta_input_same_result_deterministic |
| require readiness | gate meta | test_require_readiness_gates_meta |

7 tests, all passing.
