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


class ProviderErrorCode(Enum):
    """Categorized provider failure causes — normalized across vendors.

    Spec (TASK-006 \u00a72.6) requires: TIMEOUT, RATE_LIMIT, AUTHENTICATION_ERROR,
    INVALID_REQUEST, MODEL_UNAVAILABLE, PROVIDER_ERROR, UNKNOWN. ``AUTH`` and
    ``UNAVAILABLE`` are kept as backward-compat aliases.
    """

    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    AUTH = "auth"  # alias for AUTHENTICATION_ERROR (kept for compat)
    AUTHENTICATION_ERROR = "authentication_error"
    UNAVAILABLE = "unavailable"  # alias for MODEL_UNAVAILABLE (kept for compat)
    MODEL_UNAVAILABLE = "model_unavailable"
    INVALID_REQUEST = "invalid_request"
    PROVIDER_ERROR = "provider_error"
    UNKNOWN = "unknown"


class ProviderError(Exception):
    """Raised when a provider cannot fulfill a request."""

    # legacy alias -> canonical
    _ALIAS = {"auth": "authentication_error", "unavailable": "model_unavailable"}

    def __init__(self, message: str, code: "ProviderErrorCode" = None, cause: Exception = None):
        super().__init__(message)
        if code is None:
            code = ProviderErrorCode.UNKNOWN
        # normalize alias enums/strings to canonical code
        raw = code.value if isinstance(code, ProviderErrorCode) else str(code)
        canonical = self._ALIAS.get(raw, raw)
        # map back to enum member
        for m in ProviderErrorCode:
            if m.value == canonical:
                code = m
                break
        self.code = code
        self.cause = cause


class ModelCapability(Enum):
    """What a model can do.

    Core capabilities used by deterministic selection; extra routing signals
    (vision, reasoning, tool_calling, structured_output) are carried in
    :class:`ModelMetadata` fields, not as enum members, so callers can filter
    without hard-coding a vendor list.
    """

    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    FUNCTION_CALLING = "function_calling"
    CODE_GENERATION = "code_generation"
    JSON_MODE = "json_mode"
    # Extended routing signals also available as capabilities for symmetry
    VISION = "vision"
    REASONING = "reasoning"
    TOOL_CALLING = "tool_calling"
    STRUCTURED_OUTPUT = "structured_output"


@dataclass
class ModelMetadata:
    """Descriptive, comparable metadata for a model.

    Carries all fields the TASK-006 §2.4 routing primitive needs (id, provider,
    version, context_window, latency_class, reasoning/coding/vision/tool_calling/
    structured_output, availability, offline) plus the pricing fields consumed
    by :meth:`UsageRecord.estimate`.
    """

    model_id: str
    provider: str
    version: str = "1.0.0"
    capabilities: Sequence[ModelCapability] = field(default_factory=list)
    context_window: int = 8192
    max_output_tokens: int = 2048
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    # Routing signals (TASK-006 §2.4) — defaults keep backward compat
    latency_class: str = "standard"  # fast | standard | slow
    availability: str = "available"  # available | limited | unavailable
    reasoning: bool = False
    coding: bool = False
    vision: bool = False
    tool_calling: bool = False
    structured_output: bool = False
    offline: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    def supports(self, cap: ModelCapability) -> bool:
        # Also honour routing booleans as implicit capabilities for selection
        cap_to_attr = {
            ModelCapability.TOOL_CALLING: "tool_calling",
            ModelCapability.VISION: "vision",
            ModelCapability.REASONING: "reasoning",
            ModelCapability.STRUCTURED_OUTPUT: "structured_output",
            ModelCapability.CODE_GENERATION: "coding",
        }
        if cap in cap_to_attr and getattr(self, cap_to_attr[cap], False):
            return True
        return cap in self.capabilities

    def satisfies(self, capabilities: Sequence[ModelCapability]) -> bool:
        return all(self.supports(c) for c in capabilities)


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
