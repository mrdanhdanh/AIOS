# Test Matrix — TASK-114

| Scenario | Expected | Test |
| -------- | -------- | ---- |
| retry bounded | không loop vô hạn (T005) | test_t114_retry_bounded |
| timeout hết | fail-closed (T078) | test_t114_timeout_fail_closed |
| stream chunk | provenance đầy đủ (T001) | test_t114_streaming_provenance |
| cancel | giải phóng resource (T005) | test_t114_cancellation_releases |
| retry vượt max | reject (fail-closed) | test_t114_retry_exhausted_reject |
| cùng config + failure | cùng behavior (deterministic) | test_t114_deterministic_behavior |

6 tests, all passing.
