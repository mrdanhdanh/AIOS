"""Observability hooks for runtime hardening (TASK-065).

Provides a thin, fail-safe facade over :mod:`aios.core.logging` and
:mod:`aios.observability` metrics. Imports of the metrics backend are guarded
so the runtime degrades gracefully when observability is unavailable. Every
failure path in the hardening modules emits a trace through this facade.

Layering: runtime layer — imports ``aios.core`` (unknown) and
``aios.observability`` (unknown) only; never trips ARCH-004.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from aios.core.logging import get_logger

__all__ = ["ObservabilityHook", "ObservabilityError"]

# Safe import of the metrics backend (unknown layer — never trips ARCH-004).
try:  # pragma: no cover - import guard
    from aios.observability import MetricsCollector  # type: ignore
except Exception:  # pragma: no cover - optional backend
    MetricsCollector = None  # type: ignore


class ObservabilityError(Exception):
    """Raised on observability facade errors."""


@dataclass
class _TraceRecord:
    component: str
    level: str
    message: str
    extra: Dict[str, Any] = field(default_factory=dict)


class ObservabilityHook:
    """Emit structured JSON logs + metrics on every failure path.

    Deterministic: identical ``(component, error, extra)`` inputs produce
    identical log lines and metric increments — no randomness, no wall-clock
    dependency in the emitted payload beyond the monotonic counter.
    """

    def __init__(self, *, component: str = "runtime", metrics: Any = None) -> None:
        self._component = component
        self._logger = get_logger(f"runtime.{component}")
        if metrics is None and MetricsCollector is not None:
            try:
                metrics = MetricsCollector()
            except Exception:  # pragma: no cover
                metrics = None
        self._metrics = metrics
        self._lock = threading.RLock()
        self._traces: list[_TraceRecord] = []

    # ------------------------------------------------------------------ #
    def trace_failure(
        self,
        error: BaseException | str,
        *,
        component: Optional[str] = None,
        evidence_ref: Optional[str] = None,
        **extra: Any,
    ) -> None:
        """Emit a structured failure trace (JSON log + metric)."""
        comp = component or self._component
        message = str(error)
        rec_extra = dict(extra)
        if evidence_ref is not None:
            rec_extra["evidence_ref"] = evidence_ref
        rec = _TraceRecord(
            component=comp, level="ERROR", message=message, extra=rec_extra
        )
        with self._lock:
            self._traces.append(rec)
        self._logger.error(
            message,
            extra={"extra": {"component": comp, "evidence_ref": evidence_ref, **extra}},
        )
        if self._metrics is not None:
            try:
                self._metrics.record_execution(success=False, latency_ms=0.0)
                if evidence_ref is not None:
                    self._metrics.record_custom(f"failure.{comp}", message)
            except Exception:  # pragma: no cover - never break the caller
                pass

    def trace_event(
        self,
        message: str,
        *,
        level: str = "INFO",
        component: Optional[str] = None,
        **extra: Any,
    ) -> None:
        comp = component or self._component
        getattr(self._logger, level.lower(), self._logger.info)(
            message, extra={"extra": {"component": comp, **extra}}
        )

    def record_metric(self, name: str, value: Any) -> None:
        if self._metrics is not None:
            try:
                self._metrics.record_custom(name, value)
            except Exception:  # pragma: no cover
                pass

    def traces(self) -> list[_TraceRecord]:
        with self._lock:
            return list(self._traces)
