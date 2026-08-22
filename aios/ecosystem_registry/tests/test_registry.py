"""Tests for TASK-046 Ecosystem Registry (search, trust, version resolution, checksum)."""

from __future__ import annotations

from aios.ecosystem_registry.contracts import RegistryEntry, RegistryStatus, TrustState
from aios.ecosystem_registry.registry import EcosystemRegistry


def _entry(name: str, version: str, caps: list[str], platform: str = "any") -> RegistryEntry:
    return RegistryEntry(name=name, version=version, capabilities=caps, platform=platform)


def test_register_computes_checksum() -> None:
    reg = EcosystemRegistry()
    e = reg.register(_entry("ext", "1.0.0", ["cap1"]))
    assert e.checksum != ""


def test_search_by_capability_and_trust() -> None:
    reg = EcosystemRegistry()
    e = reg.register(_entry("ext", "1.0.0", ["cap1"]))
    reg.approve(e.entry_id)
    reg.set_trust(e.entry_id, TrustState.CERTIFIED)
    found = reg.search(capability="cap1", trust=TrustState.CERTIFIED)
    assert len(found) == 1
    assert found[0].entry_id == e.entry_id


def test_resolve_version_latest_compatible() -> None:
    reg = EcosystemRegistry()
    a = reg.register(_entry("ext", "1.0.0", ["cap1"]))
    b = reg.register(_entry("ext", "1.2.0", ["cap1"]))
    reg.approve(a.entry_id); reg.set_trust(a.entry_id, TrustState.CERTIFIED)
    reg.approve(b.entry_id); reg.set_trust(b.entry_id, TrustState.CERTIFIED)
    resolved = reg.resolve_version("ext", "1.0.0")
    assert resolved is not None and resolved.version == "1.2.0"


def test_resolve_version_requires_certified() -> None:
    reg = EcosystemRegistry()
    e = reg.register(_entry("ext", "1.0.0", ["cap1"]))
    reg.approve(e.entry_id)  # not certified
    assert reg.resolve_version("ext", "1.0.0") is None
