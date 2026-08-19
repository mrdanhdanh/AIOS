"""Automated tests for the provider registry + selection (TASK-006)."""

import pytest

from aios.runtime.providers.adapters import MockProvider, OpenAIProvider, OllamaProvider
from aios.runtime.providers.contract import (
    CompletionRequest,
    ModelCapability,
    ModelMetadata,
)
from aios.runtime.providers.registry import (
    ProviderRegistry,
    RegistryError,
    select_model,
)


def _registry():
    r = ProviderRegistry()
    r.register_provider(OpenAIProvider())
    r.register_provider(OllamaProvider())
    return r


def test_registry_defaults_to_mock():
    r = ProviderRegistry()
    assert "mock" in r.list_providers()
    assert r.list_models(offline_only=True)[0].provider == "mock"


def test_registry_register_and_list():
    r = _registry()
    names = r.list_providers()
    assert set(names) == {"mock", "openai", "ollama"}
    assert len(r.list_models()) >= 3


def test_registry_get_provider_and_model():
    r = _registry()
    assert r.get_provider("openai").name == "openai"
    mid = r.get_model("gpt-4o-mini").model_id
    assert mid == "gpt-4o-mini"


def test_registry_unknown_provider_raises():
    r = ProviderRegistry()
    with pytest.raises(RegistryError):
        r.get_provider("nope")


def test_select_model_by_capability():
    models = [
        ModelMetadata(model_id="a", provider="x", capabilities=[ModelCapability.TEXT_GENERATION]),
        ModelMetadata(model_id="b", provider="y",
                      capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.EMBEDDING]),
    ]
    chosen = select_model(models, [ModelCapability.EMBEDDING])
    assert chosen.model_id == "b"


def test_select_model_offline_first():
    models = [
        ModelMetadata(model_id="online", provider="x", offline=False, cost_per_1k_input=0.0),
        ModelMetadata(model_id="offline", provider="y", offline=True, cost_per_1k_input=5.0),
    ]
    chosen = select_model(models, offline_first=True)
    assert chosen.model_id == "offline"


def test_select_model_cost_tiebreak():
    models = [
        ModelMetadata(model_id="pricey", provider="x", cost_per_1k_input=2.0),
        ModelMetadata(model_id="cheap", provider="y", cost_per_1k_input=0.5),
    ]
    chosen = select_model(models, offline_first=False)
    assert chosen.model_id == "cheap"


def test_select_model_prefer_wins():
    models = [
        ModelMetadata(model_id="other", provider="x", offline=True),
        ModelMetadata(model_id="wanted", provider="y", offline=False),
    ]
    chosen = select_model(models, prefer="wanted")
    assert chosen.model_id == "wanted"


def test_select_model_none_when_no_capability():
    models = [ModelMetadata(model_id="a", provider="x",
                            capabilities=[ModelCapability.TEXT_GENERATION])]
    assert select_model(models, [ModelCapability.EMBEDDING]) is None


def test_registry_complete_records_call():
    r = ProviderRegistry()
    res = r.complete(CompletionRequest(prompt="hi"))
    assert r.call_count == 1
    assert "hi" in res.text


def test_registry_select_routes_by_capability():
    r = _registry()
    # Mock lacks FUNCTION_CALLING; selection must route to openai/ollama.
    chosen = r.select(capabilities=[ModelCapability.FUNCTION_CALLING])
    assert chosen.provider in ("openai", "ollama")
    assert ModelCapability.FUNCTION_CALLING in chosen.capabilities


def test_registry_complete_with_explicit_mock_model():
    r = ProviderRegistry()
    res = r.complete(CompletionRequest(prompt="hello"),
                     model_id="mock-small")
    assert r.call_count == 1
    assert res.provider == "mock"


def test_registry_swap_provider_via_contract():
    # The mock can be swapped for another offline provider without code change.
    r = ProviderRegistry()
    r.register_provider(MockProvider(model_id="mock2"))
    assert any(m.model_id == "mock2" for m in r.list_models())
