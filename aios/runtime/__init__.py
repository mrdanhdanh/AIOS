"""AIOS Runtime services (M1, TASK-004 / TASK-005).

The Runtime is the control substrate: agents/workers access capabilities only
through it. TASK-004 establishes the five independent runtime services:

    context    — six context types + hierarchical context store
    audit      — append-only, hash-chained audit trail
    artifact   — content-addressable artifacts (checksum + SemVer)
    permission — permission scopes + broker
    policy     — deterministic policy pre-check (decides before execution)

TASK-005 adds execution, scheduler, state, resource, and the RuntimeKernel that
wires everything together.

TASK-006 adds the vendor-neutral model contract + provider registry
(``providers``): providers implement :class:`ProviderAdapter` and are selected
by capability/metadata, so AIOS is never locked to one LLM vendor and runs
offline-first via :class:`MockProvider`.

Layering: ``agent -> orchestrator -> runtime -> capability -> tool``.
"""

from .artifact import Artifact, ArtifactError, ArtifactStore
from .audit import AuditError, AuditEvent, AuditStatus, AuditTrail
from .context import ContextError, ContextStore, ContextType, RuntimeContext
from .execution import (
    ExecutionError,
    ExecutionOutcome,
    ExecutionReport,
    Executor,
    StepHandler,
    StepResult,
)
from .kernel import KernelError, RuntimeKernel
from .permission import Permission, PermissionBroker, PermissionScope
from .policy import (
    PolicyDecision,
    PolicyEngine,
    PolicyRequest,
    PolicyResult,
    PolicyRule,
)
from .resource import GrantStatus, ResourceError, ResourceGrant, ResourcePool
from .scheduler import RequestStatus, ScheduledRequest, Scheduler, SchedulerError
from .state import ExecutionState, RunStatus, StateError, StateStore
from .providers import (
    CompletionRequest,
    CompletionResult,
    ModelCapability,
    ModelMetadata,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
    ProviderAdapter,
    ProviderError,
    ProviderErrorCode,
    ProviderRegistry,
    RegistryError,
    UsageRecord,
    select_model,
)

__all__ = [
    # context
    "ContextError",
    "ContextType",
    "RuntimeContext",
    "ContextStore",
    # audit
    "AuditError",
    "AuditStatus",
    "AuditEvent",
    "AuditTrail",
    # artifact
    "ArtifactError",
    "Artifact",
    "ArtifactStore",
    # permission
    "PermissionScope",
    "Permission",
    "PermissionBroker",
    # policy
    "PolicyDecision",
    "PolicyRequest",
    "PolicyRule",
    "PolicyResult",
    "PolicyEngine",
    # execution
    "ExecutionError",
    "ExecutionOutcome",
    "StepResult",
    "ExecutionReport",
    "StepHandler",
    "Executor",
    # scheduler
    "SchedulerError",
    "RequestStatus",
    "ScheduledRequest",
    "Scheduler",
    # state
    "StateError",
    "RunStatus",
    "ExecutionState",
    "StateStore",
    # resource
    "ResourceError",
    "GrantStatus",
    "ResourceGrant",
    "ResourcePool",
    # kernel
    "KernelError",
    "RuntimeKernel",
    # providers (TASK-006)
    "ProviderError",
    "ProviderErrorCode",
    "ModelCapability",
    "ModelMetadata",
    "UsageRecord",
    "CompletionRequest",
    "CompletionResult",
    "ProviderAdapter",
    "MockProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "RegistryError",
    "ProviderRegistry",
    "select_model",
]
