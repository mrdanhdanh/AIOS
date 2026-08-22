# TASK-065 — Test

## How to run
```
python -m pytest aios/runtime -q
```

## What is covered
- `test_health.py` — `RuntimeHealth` contract + `HealthMonitor` aggregation/overall.
- `test_observability.py` — fail-safe import, `trace_failure` emits JSON log + metric, determinism.
- `test_config_guard.py` — valid config passes; invalid (timeout/ttl/dir) raises `ConfigValidationError` (fail-closed); `ConfigGuard.start()` refuses.
- `test_retry.py` — bounded retry recovers on transient error; exhaustion raises `RetryBudgetExceeded` and calls `escalate`; non-retryable error stops immediately; deterministic behaviour.
- `test_resource_guard.py` — `guard()` returns False on exhaustion (degrade safe) and emits trace; `utilization`/`is_exhausted` correct; unknown resource refused safely.
- Extended `test_execution.py` / `test_kernel.py` remain green (optional params default `None`).
