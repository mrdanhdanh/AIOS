# TASK-021 — Observability + Architecture Health

## Objective
Build architecture-aware observability: metrics collection, audit with provenance, prompt history, performance profiler, system doctor, and architecture health monitoring.

## Scope
### In scope
- Metrics collector (execution, resource, model, workflow)
- Audit service with provenance tracking
- Prompt history recorder
- Performance profiler
- System health doctor (PASS/WARNING/ERROR/UNKNOWN)
- Architecture health (contract/layer/dependency/capability/permission violations)

### Out of scope
- Distributed tracing (M7)
- External monitoring integration
- Alerting rules engine

## Deliverables
- `aios/observability/__init__.py`
- `aios/observability/metrics.py` — metrics collector
- `aios/observability/audit.py` — audit with provenance
- `aios/observability/prompt_history.py` — prompt history
- `aios/observability/profiler.py` — performance profiler
- `aios/observability/doctor.py` — system health doctor
- `aios/observability/arch_health.py` — architecture health
- `aios/observability/tests/` — comprehensive tests

## Acceptance Criteria
- AC-021-01: Runtime metrics collected
- AC-021-02: Audit has provenance
- AC-021-03: Prompt history traceable
- AC-021-04: Performance bottleneck identifiable
- AC-021-05: Doctor distinguishes PASS/WARNING/ERROR/UNKNOWN
- AC-021-06: Architecture Health detects contract violations
- AC-021-07: Detects layer violations
- AC-021-08: Detects dependency violations
- AC-021-09: Detects capability/permission violations
- AC-021-10: Observability doesn't become control plane
- AC-021-11: M0–M3 regression PASS

## Dependencies
- TASK-020 (Upgrade Pipeline)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
