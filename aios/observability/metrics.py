"""Metrics collector — collects runtime, model, workflow, and resource metrics.

AC-021-01: Runtime metrics collected.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricSnapshot:
    """A snapshot of collected metrics."""

    timestamp: float = field(default_factory=time.time)
    execution_count: int = 0
    execution_success: int = 0
    execution_failure: int = 0
    execution_latency_ms: float = 0.0
    model_calls: int = 0
    model_tokens: int = 0
    model_cost: float = 0.0
    model_latency_ms: float = 0.0
    model_failures: int = 0
    workflow_duration_ms: float = 0.0
    workflow_node_failures: int = 0
    resource_cpu: float = 0.0
    resource_memory_mb: float = 0.0
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "execution_count": self.execution_count,
            "execution_success": self.execution_success,
            "execution_failure": self.execution_failure,
            "execution_latency_ms": self.execution_latency_ms,
            "model_calls": self.model_calls,
            "model_tokens": self.model_tokens,
            "model_cost": self.model_cost,
            "model_latency_ms": self.model_latency_ms,
            "model_failures": self.model_failures,
            "workflow_duration_ms": self.workflow_duration_ms,
            "workflow_node_failures": self.workflow_node_failures,
            "resource_cpu": self.resource_cpu,
            "resource_memory_mb": self.resource_memory_mb,
            "custom": self.custom,
        }


class MetricsCollector:
    """Thread-safe metrics collector for runtime observability.

    AC-021-01: Runtime metrics collected.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._snapshots: list[MetricSnapshot] = []
        self._current = MetricSnapshot()
        self._start_time = time.time()

    def record_execution(self, success: bool, latency_ms: float = 0.0) -> None:
        """Record an execution event."""
        with self._lock:
            self._current.execution_count += 1
            if success:
                self._current.execution_success += 1
            else:
                self._current.execution_failure += 1
            self._current.execution_latency_ms += latency_ms

    def record_model_call(
        self,
        tokens: int = 0,
        cost: float = 0.0,
        latency_ms: float = 0.0,
        success: bool = True,
    ) -> None:
        """Record a model call."""
        with self._lock:
            self._current.model_calls += 1
            self._current.model_tokens += tokens
            self._current.model_cost += cost
            self._current.model_latency_ms += latency_ms
            if not success:
                self._current.model_failures += 1

    def record_workflow(
        self,
        duration_ms: float = 0.0,
        node_failures: int = 0,
    ) -> None:
        """Record workflow execution."""
        with self._lock:
            self._current.workflow_duration_ms += duration_ms
            self._current.workflow_node_failures += node_failures

    def record_resource(self, cpu: float = 0.0, memory_mb: float = 0.0) -> None:
        """Record resource usage."""
        with self._lock:
            self._current.resource_cpu = cpu
            self._current.resource_memory_mb = memory_mb

    def record_custom(self, name: str, value: Any) -> None:
        """Record a custom metric."""
        with self._lock:
            self._current.custom[name] = value

    def snapshot(self) -> MetricSnapshot:
        """Take a snapshot of current metrics and reset counters."""
        with self._lock:
            snap = MetricSnapshot(
                timestamp=time.time(),
                execution_count=self._current.execution_count,
                execution_success=self._current.execution_success,
                execution_failure=self._current.execution_failure,
                execution_latency_ms=self._current.execution_latency_ms,
                model_calls=self._current.model_calls,
                model_tokens=self._current.model_tokens,
                model_cost=self._current.model_cost,
                model_latency_ms=self._current.model_latency_ms,
                model_failures=self._current.model_failures,
                workflow_duration_ms=self._current.workflow_duration_ms,
                workflow_node_failures=self._current.workflow_node_failures,
                resource_cpu=self._current.resource_cpu,
                resource_memory_mb=self._current.resource_memory_mb,
                custom=dict(self._current.custom),
            )
            self._snapshots.append(snap)
            self._current = MetricSnapshot()
            return snap

    def get_current(self) -> MetricSnapshot:
        """Get current metrics without resetting."""
        with self._lock:
            return MetricSnapshot(
                timestamp=time.time(),
                execution_count=self._current.execution_count,
                execution_success=self._current.execution_success,
                execution_failure=self._current.execution_failure,
                execution_latency_ms=self._current.execution_latency_ms,
                model_calls=self._current.model_calls,
                model_tokens=self._current.model_tokens,
                model_cost=self._current.model_cost,
                model_latency_ms=self._current.model_latency_ms,
                model_failures=self._current.model_failures,
                workflow_duration_ms=self._current.workflow_duration_ms,
                workflow_node_failures=self._current.workflow_node_failures,
                resource_cpu=self._current.resource_cpu,
                resource_memory_mb=self._current.resource_memory_mb,
                custom=dict(self._current.custom),
            )

    def get_history(self) -> list[MetricSnapshot]:
        """Get all snapshots."""
        with self._lock:
            return list(self._snapshots)

    def uptime_seconds(self) -> float:
        return time.time() - self._start_time
