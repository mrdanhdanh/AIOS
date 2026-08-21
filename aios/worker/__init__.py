"""AIOS Worker Plane — business execution layer above Orchestrator (TASK-013, M2).

Workers receive orchestrated tasks, use allowed Capabilities and return
structured Result + Evidence. They never bypass Runtime/Capability/Policy.

Architecture:
    Request -> Decision Pipeline -> Goal/Task -> Worker -> Capability -> Policy/Permission -> Runtime -> Tool

Workers:
    GeneralWorker      — research/summarize/transform/inspect/coordinate
    CoderWorker        — inspect/edit/run tests/analyze/refactor (no subprocess/open/requests)
    DoctorWorker       — diagnose task failure, recommend recovery (no auto-remediation)
    SystemDoctorWorker — runtime/service/dependency health, architecture violations

Layering: ``worker`` layer — may import ``capability`` + ``unknown`` only.
Never imports ``runtime``/``orchestrator``/``agent``/``tool`` directly.

Components:
    contract   — WorkerContract, WorkerRequest, WorkerContext, WorkerResult, WorkerEvidence
    lifecycle  — WorkerStatus, WorkerHealth, WorkerLifecycle
    registry   — WorkerRegistry
    router     — WorkerRouter
    execution  — BaseWorker (capability-only, permission-gated)
    workers    — GeneralWorker, CoderWorker, DoctorWorker, SystemDoctorWorker
"""

from .contract import (
    WorkerContract,
    WorkerContext,
    WorkerError,
    WorkerEvidence,
    WorkerRequest,
    WorkerResult,
    WorkerResultStatus,
    WorkerType,
    compute_hash,
)
from .execution import (
    BaseWorker,
    CapabilityAccessError,
    PermissionBoundaryError,
    WorkerExecutionError,
)
from .lifecycle import WorkerHealth, WorkerLifecycle, WorkerLifecycleError, WorkerStatus
from .registry import RegisteredWorker, WorkerRegistry, WorkerRegistryError
from .router import RoutingDecision, RoutingRequest, WorkerRouter, WorkerRouterError
from .workers import (
    CoderWorker,
    DoctorWorker,
    GeneralWorker,
    SystemDoctorWorker,
    DEFAULT_CODER_CONTRACT,
    DEFAULT_DOCTOR_CONTRACT,
    DEFAULT_GENERAL_CONTRACT,
    DEFAULT_SYSTEM_DOCTOR_CONTRACT,
)

__all__ = [
    "WorkerType",
    "WorkerResultStatus",
    "WorkerContract",
    "WorkerRequest",
    "WorkerContext",
    "WorkerResult",
    "WorkerEvidence",
    "WorkerError",
    "compute_hash",
    "WorkerStatus",
    "WorkerHealth",
    "WorkerLifecycle",
    "WorkerLifecycleError",
    "RegisteredWorker",
    "WorkerRegistry",
    "WorkerRegistryError",
    "RoutingRequest",
    "RoutingDecision",
    "WorkerRouter",
    "WorkerRouterError",
    "BaseWorker",
    "WorkerExecutionError",
    "CapabilityAccessError",
    "PermissionBoundaryError",
    "GeneralWorker",
    "CoderWorker",
    "DoctorWorker",
    "SystemDoctorWorker",
    "DEFAULT_GENERAL_CONTRACT",
    "DEFAULT_CODER_CONTRACT",
    "DEFAULT_DOCTOR_CONTRACT",
    "DEFAULT_SYSTEM_DOCTOR_CONTRACT",
]
