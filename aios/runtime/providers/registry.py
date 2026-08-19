"""Provider registry + deterministic model selection (TASK-006, M1).

The registry lets AIOS swap providers through a *contract*, never by hard-coded
imports. Selection is deterministic: models are filtered by required
capabilities, then ranked by (offline-first, lower cost, model id) so the same
inputs always yield the same model — no LLM involvement.

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

import threading
from typing import Dict, List, Optional, Sequence

from .adapters import MockProvider, OllamaProvider, OpenAIProvider
from .contract import (
    CompletionRequest,
    CompletionResult,
    ModelCapability,
    ModelMetadata,
    ProviderAdapter,
    ProviderError,
)


__all__ = ["ProviderRegistry", "RegistryError", "select_model"]


class RegistryError(Exception):
    """Raised on registry usage errors."""


def select_model(
    models: Sequence[ModelMetadata],
    capabilities: Sequence[ModelCapability] = (),
    *,
    offline_first: bool = True,
    prefer: Optional[str] = None,
) -> Optional[ModelMetadata]:
    """Deterministic model selection.

    Order of precedence:
      1. must satisfy all ``capabilities`` (else excluded);
      2. if ``prefer`` is set and matches a candidate, that one wins;
      3. offline models rank before online (when ``offline_first``);
      4. lower combined cost ranks higher;
      5. tie-break by model id (lexicographic) for stability.
    Returns ``None`` if no model satisfies the capabilities.
    """
    candidates = [m for m in models if m.satisfies(capabilities)]
    if not candidates:
        return None
    if prefer:
        for m in candidates:
            if m.model_id == prefer or m.provider == prefer:
                return m
    ranked = sorted(
        candidates,
        key=lambda m: (
            0 if (m.offline and offline_first) else 1,
            round(m.cost_per_1k_input + m.cost_per_1k_output, 6),
            m.model_id,
        ),
    )
    return ranked[0]


class ProviderRegistry:
    """Registry of provider adapters + their advertised models."""

    def __init__(self, *, call_log: Optional[list] = None) -> None:
        self._providers: Dict[str, ProviderAdapter] = {}
        self._models: Dict[str, ModelMetadata] = {}
        self._model_to_provider: Dict[str, str] = {}
        self._call_log: List[CompletionRequest] = list(call_log) if call_log is not None else []
        self._lock = threading.RLock()
        # Default offline provider so the runtime works with zero config.
        self.register_provider(MockProvider())

    # ------------------------------------------------------------------ #
    def register_provider(self, provider: ProviderAdapter) -> None:
        if not isinstance(provider, ProviderAdapter):
            raise RegistryError("provider must implement ProviderAdapter")
        with self._lock:
            self._providers[provider.name] = provider
            for meta in provider.list_models():
                self._models[meta.model_id] = meta
                self._model_to_provider[meta.model_id] = provider.name

    def get_provider(self, name: str) -> ProviderAdapter:
        with self._lock:
            p = self._providers.get(name)
        if p is None:
            raise RegistryError(f"unknown provider: {name!r}")
        return p

    def list_providers(self) -> List[str]:
        with self._lock:
            return sorted(self._providers.keys())

    def list_models(
        self,
        capability: Optional[ModelCapability] = None,
        offline_only: bool = False,
    ) -> List[ModelMetadata]:
        with self._lock:
            models = list(self._models.values())
        if capability is not None:
            models = [m for m in models if m.supports(capability)]
        if offline_only:
            models = [m for m in models if m.offline]
        return models

    def get_model(self, model_id: str) -> ModelMetadata:
        with self._lock:
            m = self._models.get(model_id)
        if m is None:
            raise RegistryError(f"unknown model: {model_id!r}")
        return m

    # ------------------------------------------------------------------ #
    def select(
        self,
        capabilities: Sequence[ModelCapability] = (),
        *,
        offline_first: bool = True,
        prefer: Optional[str] = None,
    ) -> ModelMetadata:
        chosen = select_model(
            self.list_models(),
            capabilities,
            offline_first=offline_first,
            prefer=prefer,
        )
        if chosen is None:
            raise RegistryError("no model satisfies the requested capabilities")
        return chosen

    def complete(
        self, request: CompletionRequest, model_id: Optional[str] = None
    ) -> CompletionResult:
        """Complete via a specific model, or select one deterministically."""
        self._call_log.append(request)
        if model_id is None:
            model_id = self.select(request.capabilities).model_id
        with self._lock:
            provider_name = self._model_to_provider.get(model_id)
            provider = self._providers.get(provider_name) if provider_name else None
        if provider is None:
            raise RegistryError(f"no provider for model {model_id!r}")
        return provider.complete(request)

    @property
    def call_count(self) -> int:
        return len(self._call_log)

    def reset_calls(self) -> None:
        self._call_log.clear()
