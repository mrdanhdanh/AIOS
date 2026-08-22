# TASK-069 Implementation

Real code lives in `aios/reliability/`:

- `slo.py` — `SLOMetric`, `SLORegistry`, `ErrorBudget` (fail-closed burn-rate guard).
- `circuit_breaker.py` — `CircuitBreaker` (CLOSED/OPEN/HALF_OPEN).
- `retry.py` — re-export `BoundedRetry` from `aios.runtime.retry` (T065).
- `integration.py` — health probe (`aios.core.healthcheck`) + optional durable/kill-switch bridges.

Tests: `aios/reliability/tests/test_reliability.py`.
