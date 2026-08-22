# TASK-065 — Breakdown

- [x] Step 1 — Create `aios/runtime/health.py` (`RuntimeHealth`, `HealthMonitor`).
- [x] Step 2 — Create `aios/runtime/observability.py` (fail-safe JSON log + metrics facade).
- [x] Step 3 — Create `aios/runtime/config_guard.py` (fail-closed `require_valid_config` / `ConfigGuard`).
- [x] Step 4 — Create `aios/runtime/retry.py` (`BoundedRetry` + `RetryConfig` + `RetryBudgetExceeded`).
- [x] Step 5 — Extend `aios/runtime/resource.py` with `ResourceGuard` (exhaustion → degrade safe).
- [x] Step 6 — Wire `Executor.observability` hook on failure paths; `RuntimeKernel` refuses invalid config.
- [x] Step 7 — Write tests under `aios/runtime/tests/` (`test_health.py`, `test_observability.py`, `test_config_guard.py`, `test_retry.py`, `test_resource_guard.py`).
- [x] Step 8 — Run `python -m pytest aios/runtime -q` and confirm green.
