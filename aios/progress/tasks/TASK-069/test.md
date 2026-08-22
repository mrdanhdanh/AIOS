# TASK-069 — Test

## How to run
```
python -m pytest aios/reliability -q
```

## What is covered
- SLO registry + error budget fail-closed (AC1, AC2, AC5, AC6).
- Circuit breaker open on failure rate (AC3).
- Bounded retry recover + escalate (AC4, no infinite loop).
- Health probe integration (AC7).
