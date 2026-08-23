# TASK-139 — Task Breakdown

1. Định nghĩa `TestVerdict` (pass/fail) + `TestResult` (content_hash, T078).
2. Định nghĩa `TestRun` (execution/sandbox/workspace/policy refs + results).
3. `TestRunner.__init__` inject contract/sandbox/workspace/policy/dispatcher.
4. `run` fail-closed: sandbox-only + policy enforce + contract validate + dispatch.
5. Deterministic result từ response (exit_code -> verdict).
6. `provenance`/content_hash (T001/T078).
7. Tests (`test_test_runner.py`): 6 tests.
8. Chạy pytest + gate_check.
