# Breakdown — TASK-226

- `aios/runtime/retry_guard.py` — `RetryGuard` class (observe/should_stop/report/reset/count).
- `aios/runtime/tests/test_retry_guard.py` — 7 unit tests.
- Optional wiring note: orchestrator loop calls `retry_guard.observe(sig)` and checks `should_stop` before retrying.
