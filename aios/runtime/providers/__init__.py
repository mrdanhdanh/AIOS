"""Model contract + provider registry (TASK-006, M1).

Vendor-neutral model access. AIOS is never locked to one LLM vendor: providers
implement :class:`~aios.runtime.providers.contract.ProviderAdapter` and are
selected by capability/metadata through
:class:`~aios.runtime.providers.registry.ProviderRegistry`.

Offline-first: the default :class:`MockProvider` runs with zero external
dependencies, so the whole stack works without network or third-party SDKs.
"""

from .adapters import MockProvider, OllamaProvider, OpenAIProvider
from .contract import (
    CompletionRequest,
    CompletionResult,
    ModelCapability,
    ModelMetadata,
    ProviderAdapter,
    ProviderError,
    ProviderErrorCode,
    UsageRecord,
)
from .registry import ProviderRegistry, RegistryError, select_model

__all__ = [
    # contract
    "ProviderError",
    "ProviderErrorCode",
    "ModelCapability",
    "ModelMetadata",
    "UsageRecord",
    "CompletionRequest",
    "CompletionResult",
    "ProviderAdapter",
    # adapters
    "MockProvider",
    "OpenAIProvider",
    "OllamaProvider",
    # registry
    "RegistryError",
    "ProviderRegistry",
    "select_model",
]
