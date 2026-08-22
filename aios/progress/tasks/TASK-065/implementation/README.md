# TASK-065 — Implementation

This folder is a **pointer** only. Real source lives under `aios/runtime/`:

- `aios/runtime/health.py` — `RuntimeHealth` dataclass + `HealthMonitor`.
- `aios/runtime/observability.py` — fail-safe JSON log + metrics facade (`ObservabilityHook`).
- `aios/runtime/config_guard.py` — fail-closed config validation (`require_valid_config`, `ConfigGuard`, `ConfigValidationError`).
- `aios/runtime/retry.py` — bounded retry with backoff + escalation (`BoundedRetry`, `RetryConfig`, `RetryBudgetExceeded`).
- `aios/runtime/resource.py` — extended with `ResourceGuard` / `ResourceExhausted` (exhaustion → degrade safe).
- `aios/runtime/execution.py` — optional `observability` hook on failure paths.
- `aios/runtime/kernel.py` — refuses to start on invalid config (`require_valid_config`).

Tests: `aios/runtime/tests/test_health.py`, `test_observability.py`,
`test_config_guard.py`, `test_retry.py`, `test_resource_guard.py`.

Run: `python -m pytest aios/runtime -q`
