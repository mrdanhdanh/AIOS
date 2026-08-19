"""Automated tests for the model/provider contract (TASK-006)."""

import pytest

from aios.runtime.providers.contract import (
    CompletionRequest,
    ModelCapability,
    ModelMetadata,
    ProviderError,
    ProviderErrorCode,
    UsageRecord,
)


def test_model_metadata_capabilities():
    m = ModelMetadata(
        model_id="m1", provider="mock",
        capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
    )
    assert m.supports(ModelCapability.TEXT_GENERATION)
    assert not m.supports(ModelCapability.EMBEDDING)
    assert m.satisfies([ModelCapability.TEXT_GENERATION, ModelCapability.CHAT])
    assert not m.satisfies([ModelCapability.TEXT_GENERATION, ModelCapability.EMBEDDING])


def test_usage_estimate_charges_cost():
    m = ModelMetadata(model_id="m1", provider="mock",
                      cost_per_1k_input=1.0, cost_per_1k_output=2.0)
    u = UsageRecord.estimate("x" * 400, "y" * 400, m)
    assert u.prompt_tokens == 100
    assert u.completion_tokens == 100
    assert u.total_tokens == 200
    assert u.cost == pytest.approx(100 / 1000 * 1.0 + 100 / 1000 * 2.0)


def test_provider_error_code():
    err = ProviderError("boom", code=ProviderErrorCode.RATE_LIMIT)
    assert err.code == ProviderErrorCode.RATE_LIMIT
    assert "boom" in str(err)


def test_completion_request_defaults():
    req = CompletionRequest(prompt="hi")
    assert req.max_tokens == 512
    assert req.temperature == 0.0
    assert req.capabilities == []


def test_model_capability_values():
    assert {c.value for c in ModelCapability} >= {
        "text_generation", "chat", "embedding", "function_calling", "code_generation"
    }
