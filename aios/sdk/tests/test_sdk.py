"""Tests for SDK."""
from __future__ import annotations
from aios.sdk.contracts import SDKConfig, SDKResponse
from aios.sdk.client import AIOSClient

class TestSDK:
    def test_client_config(self):
        c = AIOSClient(SDKConfig(base_url="http://test:9000"))
        assert c.config.base_url == "http://test:9000"
    def test_health(self):
        r = AIOSClient().health()
        assert r.success
        assert r.data["status"] == "ok"
    def test_execute(self):
        r = AIOSClient().execute("chat", message="hi")
        assert r.success
        assert r.data["intent"] == "chat"
    def test_list_resources(self):
        r = AIOSClient().list_resources("models")
        assert r.success
    def test_response_provenance(self):
        r = AIOSClient().execute("test")
        assert len(r.provenance) > 0


class TestSDKT043:
    def test_error_classes(self):
        from aios.sdk.contracts import (
            AuthError,
            NotFoundError,
            RateLimitError,
            TimeoutError,
            ValidationError,
        )
        for exc in (ValidationError, NotFoundError, AuthError, RateLimitError, TimeoutError):
            e = exc("boom")
            assert e.code != ""

    def test_sdk_version_compat(self):
        from aios.sdk.contracts import SDKVersion
        sdk = SDKVersion.parse("1.2.0")
        contract = SDKVersion.parse("1.1.0")
        assert sdk.is_compatible_with(contract) is True
        assert contract.is_compatible_with(sdk) is False
        assert SDKVersion.parse("2.0.0").is_compatible_with(SDKVersion.parse("1.0.0")) is False

    def test_mock_client(self):
        from aios.sdk.mock_client import MockAIOSClient
        c = MockAIOSClient(SDKConfig())
        resp = c.execute("review", target="x")
        assert resp.success is True
        assert c.executed_intents() == ["review"]

    def test_discovery(self):
        from aios.sdk.discovery import discover_contracts, discover_endpoints
        eps = discover_endpoints(SDKConfig())
        assert any(ep.endswith("/api/v1/health") for ep in eps)
        assert "AIOSClient" in discover_contracts()["client"]
