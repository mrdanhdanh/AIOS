"""Tests for ecosystem hub."""
from __future__ import annotations
import pytest
from aios.ecosystem_hub.contracts import HubEntry, HubStatus
from aios.ecosystem_hub.hub import EcosystemHub

class TestEcosystemHub:
    def test_publish(self):
        hub = EcosystemHub()
        e = hub.publish(HubEntry(name="ext1"))
        assert e.status == HubStatus.PUBLISHED
    def test_unpublish(self):
        hub = EcosystemHub()
        e = hub.publish(HubEntry(name="ext1"))
        hub.unpublish(e.entry_id)
        assert e.status == HubStatus.UNPUBLISHED
    def test_download(self):
        hub = EcosystemHub()
        e = hub.publish(HubEntry(name="ext1"))
        hub.download(e.entry_id)
        assert e.downloads == 1
    def test_not_found(self):
        hub = EcosystemHub()
        with pytest.raises(RuntimeError): hub.unpublish("nonexistent")
    def test_to_dict(self):
        e = HubEntry(name="x")
        d = e.to_dict()
        assert d["name"] == "x"
