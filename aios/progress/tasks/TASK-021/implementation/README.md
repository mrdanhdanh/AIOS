# TASK-021 Implementation — Observability + Architecture Health

Implementation lives in `aios/observability/` (M4 Platform Edition — Observability).

```
aios/observability/
  metrics.py        # MetricsCollector, MetricSnapshot
  audit.py          # AuditService, AuditEntry (hash-chained)
  prompt_history.py # PromptHistory, PromptRecord
  profiler.py       # ProfilerService, ProfileResult
  doctor.py         # DoctorService, HealthReport (13 domain doctors)
  arch_health.py    # ArchitectureHealth, ViolationReport
  health_api.py     # HealthAPI, SystemHealth (fail-closed UNKNOWN≠PASS)
  dashboard.py      # DashboardIntegration, DashboardSnapshot
  __init__.py       # re-exports
  tests/
    test_metrics.py
    test_audit.py
    test_doctor.py
    test_arch_health.py
    test_health_api.py
```

Detects contract/layer/dependency/capability/permission violations. `UNKNOWN` never promoted to `PASS` (fail-closed).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
