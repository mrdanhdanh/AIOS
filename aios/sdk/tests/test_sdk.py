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
