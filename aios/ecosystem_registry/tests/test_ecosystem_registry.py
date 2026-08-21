"""Tests for ecosystem registry."""
from __future__ import annotations
import pytest
from aios.ecosystem_registry.contracts import RegistryEntry, RegistryStatus
from aios.ecosystem_registry.registry import EcosystemRegistry

class TestEcosystemRegistry:
    def test_register(self):
        reg = EcosystemRegistry()
        e = reg.register(RegistryEntry(name="ext1"))
        assert e.name == "ext1"
    def test_approve_reject(self):
        reg = EcosystemRegistry()
        e = reg.register(RegistryEntry(name="ext1"))
        reg.approve(e.entry_id)
        assert e.status == RegistryStatus.APPROVED
        reg.reject(e.entry_id)
        assert e.status == RegistryStatus.REJECTED
    def test_list_by_status(self):
        reg = EcosystemRegistry()
        e1 = reg.register(RegistryEntry(name="a"))
        e2 = reg.register(RegistryEntry(name="b"))
        reg.approve(e1.entry_id)
        assert len(reg.list_entries(RegistryStatus.APPROVED)) == 1
    def test_not_found(self):
        reg = EcosystemRegistry()
        with pytest.raises(RuntimeError): reg.approve("nonexistent")
    def test_to_dict(self):
        e = RegistryEntry(name="x")
        d = e.to_dict()
        assert d["name"] == "x"
