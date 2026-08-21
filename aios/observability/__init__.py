"""AIOS Observability — Metrics, audit, profiler, doctor, architecture health."""

from aios.observability.arch_health import ArchitectureHealth, ViolationReport
from aios.observability.audit import AuditEntry, AuditService
from aios.observability.doctor import DoctorService, HealthReport
from aios.observability.metrics import MetricsCollector, MetricSnapshot
from aios.observability.profiler import ProfilerService, ProfileResult
from aios.observability.prompt_history import PromptHistory, PromptRecord

__all__ = [
    "MetricsCollector",
    "MetricSnapshot",
    "AuditService",
    "AuditEntry",
    "PromptHistory",
    "PromptRecord",
    "ProfilerService",
    "ProfileResult",
    "DoctorService",
    "HealthReport",
    "ArchitectureHealth",
    "ViolationReport",
]
