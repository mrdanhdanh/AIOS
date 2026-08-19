"""Concrete provider adapters: Mock (offline), OpenAI, Ollama (TASK-006, M1).

The :class:`MockProvider` is fully offline and the default for tests and the
harness. The ``openai`` and ``ollama`` adapters import their SDKs lazily so the
package imports without third-party dependencies and degrades gracefully when a
backend is unavailable.

Layering: ``runtime`` layer — relative imports only.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional

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


__all__ = ["MockProvider", "OpenAIProvider", "OllamaProvider"]


class MockProvider(ProviderAdapter):
    """Offline, deterministic provider for tests and the harness.

    Returns a canned completion derived from the prompt. Counts calls so the
    deterministic-first gate can assert ``LLM call count == 0`` when the
    deterministic path handles a request without reaching a provider.
    """

    name = "mock"

    def __init__(self, model_id: str = "mock-small", *, call_log: Optional[list] = None) -> None:
        self._model = ModelMetadata(
            model_id=model_id,
            provider="mock",
            version="1.0.0",
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
                ModelCapability.JSON_MODE,
            ],
            context_window=8192,
            max_output_tokens=2048,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            offline=True,
        )
        self._calls: List[CompletionRequest] = list(call_log) if call_log is not None else []
        self._next_responses: List[str] = []

    # -- ProviderAdapter interface -------------------------------------- #
    def list_models(self) -> List[ModelMetadata]:
        return [self._model]

    def is_offline(self) -> bool:
        return True

    def queue_response(self, text: str) -> None:
        """Inject the next completion text (for scripted tests)."""
        self._next_responses.append(text)

    @property
    def call_count(self) -> int:
        return len(self._calls)

    def complete(self, request: CompletionRequest) -> CompletionResult:
        self._calls.append(request)
        if self._next_responses:
            text = self._next_responses.pop(0)
        else:
            prompt = request.prompt or _messages_to_text(request.messages)
            text = f"[mock:{self._model.model_id}] {prompt}"
        usage = UsageRecord.estimate(
            request.prompt or _messages_to_text(request.messages),
            text,
            self._model,
        )
        return CompletionResult(
            text=text,
            model_id=self._model.model_id,
            provider=self.name,
            usage=usage,
            finish_reason="stop",
        )


class OpenAIProvider(ProviderAdapter):
    """Adapter for OpenAI-compatible chat completions (lazy SDK import)."""

    name = "openai"

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self._model = ModelMetadata(
            model_id=model_id,
            provider="openai",
            version="1.0.0",
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.FUNCTION_CALLING,
                ModelCapability.JSON_MODE,
            ],
            context_window=128000,
            max_output_tokens=4096,
            cost_per_1k_input=0.00015,
            cost_per_1k_output=0.0006,
            offline=False,
        )
        self._api_key = api_key
        self._base_url = base_url

    def list_models(self) -> List[ModelMetadata]:
        return [self._model]

    def is_offline(self) -> bool:
        return False

    def complete(self, request: CompletionRequest) -> CompletionResult:
        try:
            from openai import OpenAI  # lazy import
        except ImportError as exc:  # pragma: no cover - depends on env
            raise ProviderError(
                "openai SDK not installed; cannot use OpenAIProvider offline",
                code=ProviderErrorCode.UNAVAILABLE,
                cause=exc,
            )
        client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        try:
            resp = client.chat.completions.create(
                model=self._model.model_id,
                messages=request.messages
                or [{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            text = resp.choices[0].message.content or ""
            usage = UsageRecord(
                prompt_tokens=getattr(resp.usage, "prompt_tokens", 0),
                completion_tokens=getattr(resp.usage, "completion_tokens", 0),
                total_tokens=getattr(resp.usage, "total_tokens", 0),
            )
            return CompletionResult(
                text=text,
                model_id=self._model.model_id,
                provider=self.name,
                usage=usage,
                finish_reason="stop",
            )
        except Exception as exc:  # pragma: no cover - depends on network
            raise ProviderError(
                f"OpenAI completion failed: {exc}", cause=exc
            )


class OllamaProvider(ProviderAdapter):
    """Adapter for a local Ollama server (stdlib ``urllib`` only)."""

    name = "ollama"

    def __init__(self, model_id: str = "llama3", *, base_url: str = "http://localhost:11434") -> None:
        self._model = ModelMetadata(
            model_id=model_id,
            provider="ollama",
            version="1.0.0",
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
                ModelCapability.CODE_GENERATION,
            ],
            context_window=8192,
            max_output_tokens=2048,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            offline=False,  # local server, but not bundled offline
        )
        self._base_url = base_url.rstrip("/")

    def list_models(self) -> List[ModelMetadata]:
        return [self._model]

    def is_offline(self) -> bool:
        return False

    def complete(self, request: CompletionRequest) -> CompletionResult:
        payload = {
            "model": self._model.model_id,
            "prompt": request.prompt or _messages_to_text(request.messages),
            "stream": False,
            "options": {"temperature": request.temperature, "num_predict": request.max_tokens},
        }
        url = f"{self._base_url}/api/generate"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            text = body.get("response", "")
        except Exception as exc:
            raise ProviderError(
                f"Ollama completion failed: {exc}",
                code=ProviderErrorCode.UNAVAILABLE,
                cause=exc,
            )
        usage = UsageRecord.estimate(payload["prompt"], text, self._model)
        return CompletionResult(
            text=text,
            model_id=self._model.model_id,
            provider=self.name,
            usage=usage,
            finish_reason="stop",
        )


def _messages_to_text(messages) -> str:
    if not messages:
        return ""
    return "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages)
