"""Automated tests for the provider adapters (TASK-006)."""

import pytest

from aios.runtime.providers.adapters import (
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)
from aios.runtime.providers.contract import (
    CompletionRequest,
    ModelCapability,
    ProviderError,
    ProviderErrorCode,
)


def test_mock_provider_is_offline():
    p = MockProvider()
    assert p.is_offline()
    assert p.list_models()[0].offline is True


def test_mock_provider_completion():
    p = MockProvider()
    res = p.complete(CompletionRequest(prompt="hello"))
    assert "hello" in res.text
    assert res.model_id == "mock-small"
    assert res.provider == "mock"
    assert res.usage.total_tokens > 0


def test_mock_provider_counts_calls():
    p = MockProvider()
    p.complete(CompletionRequest(prompt="a"))
    p.complete(CompletionRequest(prompt="b"))
    assert p.call_count == 2


def test_mock_provider_queued_response():
    p = MockProvider()
    p.queue_response("canned")
    res = p.complete(CompletionRequest(prompt="ignored"))
    assert res.text == "canned"


def test_openai_provider_not_offline():
    p = OpenAIProvider()
    assert not p.is_offline()
    assert p.list_models()[0].provider == "openai"


def test_openai_provider_requires_sdk(monkeypatch):
    # Force the lazy import to fail to simulate a missing SDK.
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "openai":
            raise ImportError("no openai")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    p = OpenAIProvider()
    with pytest.raises(ProviderError) as exc:
        p.complete(CompletionRequest(prompt="hi"))
    # ProviderError normalizes legacy UNAVAILABLE -> MODEL_UNAVAILABLE
    assert exc.value.code in (ProviderErrorCode.UNAVAILABLE, ProviderErrorCode.MODEL_UNAVAILABLE)


def test_ollama_provider_not_offline():
    p = OllamaProvider()
    assert not p.is_offline()
    assert p.list_models()[0].provider == "ollama"


def test_ollama_completion_uses_urllib(monkeypatch):
    import aios.runtime.providers.adapters as adp

    payload_capture = {}

    class FakeResp:
        def read(self):
            return b'{"response": "local reply"}'

    class FakeUrlopen:
        def __init__(self, req, timeout=None):
            payload_capture["url"] = req.full_url
            payload_capture["data"] = req.data

        def __enter__(self):
            return FakeResp()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(adp.urllib.request, "urlopen", FakeUrlopen)
    p = OllamaProvider(base_url="http://localhost:11434")
    res = p.complete(CompletionRequest(prompt="hi"))
    assert res.text == "local reply"
    assert "api/generate" in payload_capture["url"]


def test_openai_and_ollama_capabilities():
    oai = OpenAIProvider().list_models()[0]
    oll = OllamaProvider().list_models()[0]
    assert ModelCapability.FUNCTION_CALLING in oai.capabilities
    assert ModelCapability.CODE_GENERATION in oll.capabilities
