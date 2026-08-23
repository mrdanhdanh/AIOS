# TASK-143 — Task Breakdown

1. Định nghĩa `ReplayRun` (execution/sandbox/policy refs + `replay_deterministic` + hashes).
2. `SecurityReplayHarness.__init__` inject contract/sandbox/policy/dispatcher.
3. `secure_run` fail-closed: sandbox-only + policy enforce + contract validate + dispatch.
4. `replay` so sánh original/replayed -> mismatch raise (fail-closed, T078).
5. `content_hash` trên `ReplayRun` (T001/T078).
6. Tests (`test_replay.py`): 6 tests.
7. Chạy pytest + gate_check.
