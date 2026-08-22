# TASK-069 — AIOS Reliability Engineering

## Objective
Thiết lập SLO và reliability controls cho AIOS: SLO definitions, error budgets,
circuit breakers và bounded retry/backoff chuẩn cho toàn hệ thống (dựa trên T065
Hardening + T066 Durable). Đây là reliability controls, không phải runtime rewrite.

## Scope
- SLO Registry + Error Budget (burn-rate guard, fail-closed).
- Circuit Breaker (open/half-open/closed).
- Bounded Retry/Backoff (reuse T065).
- Health probe integration (`aios.core.healthcheck`).
- Integration với Runtime (T065) + Durable (T066) + Kill Switch (T068).

## Deliverables
- `aios/reliability/slo.py` — `SLOMetric`, `SLORegistry`, `ErrorBudget` (fail-closed).
- `aios/reliability/circuit_breaker.py` — `CircuitBreaker`.
- `aios/reliability/retry.py` — re-export `BoundedRetry` (T065).
- `aios/reliability/integration.py` — health probe + optional durable/kill-switch bridges.
- Tests `aios/reliability/tests/test_reliability.py`.

## Acceptance Criteria
- AC1: Mọi critical path có SLO định nghĩa + đo được.
- AC2: Error budget cạn → degrade safe / stop new work (fail-closed).
- AC3: Circuit breaker mở khi failure rate vượt ngưỡng.
- AC4: Retry bounded (không infinite).
- AC5: SLO measurement có provenance evidence.
- AC6: Cùng metric + policy → cùng quyết định (deterministic).
- AC7: Tích hợp được với Runtime (T065) + Kill Switch (T068).
- AC8: Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- TASK-065 Runtime Production Hardening, TASK-066 Durable Execution 1.0.

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`. No parallel reliability system.
