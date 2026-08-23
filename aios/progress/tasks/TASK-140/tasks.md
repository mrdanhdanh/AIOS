# TASK-140 — Task Breakdown

1. Định nghĩa `BuildVerdict`/`LintVerdict` + `BuildResult`/`LintResult` (content_hash, T078).
2. Định nghĩa `BuildLintRun` (execution/sandbox/workspace/policy refs + results).
3. `BuildLintRunner.__init__` inject contract/sandbox/workspace/policy/dispatcher.
4. `run` fail-closed: sandbox-only + policy enforce + contract validate + dispatch.
5. Deterministic build/lint result từ response (exit_code -> verdict).
6. `content_hash` (T001/T078).
7. Tests (`test_build_lint.py`): 6 tests.
8. Chạy pytest + gate_check.
