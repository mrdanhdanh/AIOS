"""Reliability Engineering (M10 — TASK-069).

SLO definitions, error budgets, circuit breakers and bounded retry/backoff for
AIOS. Integrates with Runtime hardening (T065), Durable Execution (T066) and
Kill Switch (T068) via public interfaces; reuses ``aios.runtime.retry`` for the
bounded retry primitive.

Layering: ``reliability`` is an ``unknown`` (infra) layer — it only imports
peer/downward modules (core, runtime, durable, kill_switch) and never imports
``agents/``. No parallel reliability system is created; this composes on top of
Runtime + Observability.
"""

from __future__ import annotations

from aios.reliability.slo import (
    ErrorBudget,
    ErrorBudgetExhausted,
    SLORegistry,
    SLOMetric,
    SLOStatus,
)
from aios.reliability.circuit_breaker import CircuitBreaker, CircuitOpen, CircuitState
from aios.reliability.retry import BoundedRetry, RetryBudgetExceeded, RetryConfig
from aios.reliability.integration import ReliabilityProbe, register_reliability_probes

__all__ = [
    "ErrorBudget",
    "ErrorBudgetExhausted",
    "SLORegistry",
    "SLOMetric",
    "SLOStatus",
    "CircuitBreaker",
    "CircuitOpen",
    "CircuitState",
    "BoundedRetry",
    "RetryBudgetExceeded",
    "RetryConfig",
    "ReliabilityProbe",
    "register_reliability_probes",
]
