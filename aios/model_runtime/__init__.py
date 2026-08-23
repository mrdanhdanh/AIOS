"""Model Runtime (M17) — vendor-neutral model execution substrate.

Packages the eight M17 capabilities as a single, import-safe ``unknown``
(infra) layer:

* T109 Model Contracts        -> :mod:`aios.model_runtime.contracts`
* T110 Provider Registry      -> :mod:`aios.model_runtime.provider_registry`
* T111 Model Registry/Resolve -> :mod:`aios.model_runtime.model_registry`
* T112 Inference Orchestration-> :mod:`aios.model_runtime.orchestration`
* T113 Credential/Permission  -> :mod:`aios.model_runtime.security`
* T114 Retry/Timeout/Stream   -> :mod:`aios.model_runtime.resilience`
* T115 Usage/Cost/Audit       -> :mod:`aios.model_runtime.usage`
* T116 Conformance/Certify    -> :mod:`aios.model_runtime.conformance`
"""

from .contracts import (
    CapabilityDeclaration,
    ModelCapability,
    ModelContract,
    ModelContractError,
    ModelRequest,
    ModelResponse,
    PolicyBoundary,
    UsageSchema,
    validate_contract,
)
from .conformance import (
    ConformanceError,
    ConformanceResult,
    ConformanceSuite,
    ProviderCertification,
    ProviderCertifier,
)
from .model_registry import ModelRegistry, ModelRegistryError, ModelResolver, ResolveStatus
from .orchestration import (
    ExecutionStatus,
    InferenceOrchestrator,
    InferencePlan,
    OrchestrationError,
)
from .provider_registry import (
    HealthStatus,
    LifecycleEvent,
    ProviderRecord,
    ProviderRegistry,
    ProviderRegistryError,
    ProviderStatus,
)
from .resilience import (
    CancellationToken,
    ResilienceConfig,
    ResilienceError,
    ResilienceManager,
    ResilienceStatus,
    StreamChunk,
)
from .security import (
    CredentialBoundary,
    PermissionCheck,
    PolicyPrecheck,
    SecurityContext,
    SecurityError,
    SecurityGate,
)
from .usage import (
    AuditEntry,
    AuditLog,
    CostCompute,
    UsageCollector,
    UsageError,
    UsageRecord,
)

__all__ = [
    # T109
    "ModelContract",
    "ModelContractError",
    "ModelCapability",
    "UsageSchema",
    "CapabilityDeclaration",
    "ModelRequest",
    "ModelResponse",
    "PolicyBoundary",
    "validate_contract",
    # T110
    "ProviderRegistry",
    "ProviderRegistryError",
    "ProviderStatus",
    "HealthStatus",
    "ProviderRecord",
    "LifecycleEvent",
    # T111
    "ModelRegistry",
    "ModelRegistryError",
    "ModelResolver",
    "ResolveStatus",
    # T112
    "InferenceOrchestrator",
    "OrchestrationError",
    "InferencePlan",
    "ExecutionStatus",
    # T113
    "SecurityError",
    "SecurityContext",
    "CredentialBoundary",
    "PermissionCheck",
    "PolicyPrecheck",
    "SecurityGate",
    # T114
    "ResilienceError",
    "ResilienceConfig",
    "CancellationToken",
    "StreamChunk",
    "ResilienceManager",
    "ResilienceStatus",
    # T115
    "UsageError",
    "AuditEntry",
    "UsageRecord",
    "CostCompute",
    "AuditLog",
    "UsageCollector",
    # T116
    "ConformanceError",
    "ConformanceResult",
    "ConformanceSuite",
    "ProviderCertification",
    "ProviderCertifier",
]
