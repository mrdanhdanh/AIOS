# Breakdown — TASK-227

- `aios/runtime/stub_guard.py` — `StubGuard` (record/is_skip/violations/is_clean/report/reset).
- `aios/runtime/tests/test_stub_guard.py` — 7 unit tests.
- Optional wiring note: orchestrator loop records each step status and blocks DONE on violations.
