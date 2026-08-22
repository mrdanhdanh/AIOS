# TASK-055 — Test Report

## How to run
```
python -m pytest aios/autonomous_recovery/tests -q
python -m pytest aios -q
```

## Coverage
- Failure classification (7 classes).
- Circuit breaker open/half-open/close lifecycle.
- Retry → recovered; unverified → NOT_RECOVERED (fail-closed).
- Unknown failure → SAFE_STOP.
- Governor denial → NOT_RECOVERED.
- Circuit OPEN blocks recovery.
- Recovery attempt provenance recorded.

## Results
- `autonomous_recovery/tests`: 8 passed
- Architecture gate: PASS
- Status: ALL PASS
