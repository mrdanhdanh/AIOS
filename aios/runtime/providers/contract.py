"""Model/provider contracts (TASK-006, M1).

Vendor-neutral model contract. AIOS is never locked to a single LLM vendor:
every provider implements :class:`ProviderAdapter` and is selected through the
:class:`~aios.runtime.providers.registry.ProviderRegistry` by *capability* and
*metadata*, never by hard-coded imports.

All adapters are pure-Python + stdlib so the runtime stays offline-first; the
:class:`MockProvider` runs with zero external dependencies. ``openai`` /
``ollama`` adapters import their SDK lazily and degrade to a clear
:class:`ProviderError` when unavailable.

Layering: ``runtime`` layer — relative imports within the package; no
agent/orchestrator imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


__all__ = [
    "ProviderError",
    "ProviderErrorCode",
    "ModelCapability",
    "ModelMetadata",
    "UsageRecord",
    "CompletionRequest",
    "CompletionResult",
    "ProviderAdapter",
]


class ProviderError(Exception):
    """Raised when a provider cannot fulfill a request."""

    def __init__(self, message: str, code: "ProviderErrorCode" = None, cause: Exception = None):
        super().__init__(message)
        self.code = code or ProviderErrorCode.UNKNOWN
        self.cause = cause


class ProviderErrorCode(Enum):
    """Categorized provider failure causes."""

    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    AUTH = "auth"
    UNAVAILABLE = "unavailable"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN = "unknown"


class ModelCapability(Enum):
    """What a model can do."""

    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    FUNCTION_CALLING = "function_calling"
    CODE_GENERATION = "code_generation"
    JSON_MODE = "json_mode"


@dataclass
class ModelMetadata:
    """Descriptive, comparable metadata for a model."""

    model_id: str
    provider: str
    version: str = "1.0.0"
    capabilities: Sequence[ModelCapability] = field(default_factory=list)
    context_window: int = 8192
    max_output_tokens: int = 2048
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    offline: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    def supports(self, cap: ModelCapability) -> bool:
        return cap in self.capabilities

    def satisfies(self, capabilities: Sequence[ModelCapability]) -> bool:
        return all(c in self.capabilities for c in capabilities)


@dataclass
class UsageRecord:
    """Token/cost accounting for a single completion."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    cached: bool = False

    @classmethod
    def estimate(cls, prompt: str, completion: str, meta: ModelMetadata) -> "UsageRecord":
        pt = max(1, len(prompt) // 4)
        ct = max(1, len(completion) // 4)
        cost = (
            pt / 1000.0 * meta.cost_per_1k_input
            + ct / 1000.0 * meta.cost_per_1k_output
        )
        return cls(
            prompt_tokens=pt,
            completion_tokens=ct,
            total_tokens=pt + ct,
            cost=round(cost, 6),
        )


@dataclass
class CompletionRequest:
    """A request for a completion."""

    prompt: str = ""
    messages: Optional[List[Dict[str, str]]] = None
    model_hint: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.0
    capabilities: Sequence[ModelCapability] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResult:
    """A completion returned by a provider."""

    text: str
    model_id: str
    provider: str
    usage: UsageRecord
    finish_reason: str = "stop"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProviderAdapter:
    """Interface every model provider adapter implements.

    Use as a structural protocol: any object with these methods qualifies.
    The registry stores concrete adapters (Mock/OpenAI/Ollama).
    """

    name: str

    def list_models(self) -> List[ModelMetadata]:  # pragma: no cover - interface
        raise NotImplementedError

    def complete(self, request: CompletionRequest) -> CompletionResult:  # pragma: no cover
        raise NotImplementedError

    def is_offline(self) -> bool:  # pragma: no cover - interface
        raise NotImplementedError
