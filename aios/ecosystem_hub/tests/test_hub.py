"""Tests for TASK-048 Ecosystem Hub (search, compatibility, checksum, install)."""

from __future__ import annotations

from aios.ecosystem_hub.contracts import HubEntry, HubStatus
from aios.ecosystem_hub.hub import EcosystemHub
from aios.plugin_runtime.runtime import PluginRuntime


def _entry(name: str, version: str, caps: list[str]) -> HubEntry:
    return HubEntry(name=name, version=version, capabilities=caps)


def test_publish_sets_checksum_and_provenance() -> None:
    hub = EcosystemHub()
    e = hub.publish(_entry("ext", "1.0.0", ["cap1"]))
    assert e.checksum != ""
    assert any(p.startswith("hub:publish:") for p in e.provenance)


def test_search_only_published() -> None:
    hub = EcosystemHub()
    e = hub.publish(_entry("ext", "1.0.0", ["cap1"]))
    hub.unpublish(e.entry_id)
    assert hub.search(query="ext") == []


def test_search_by_capability() -> None:
    hub = EcosystemHub()
    e = hub.publish(_entry("ext", "1.0.0", ["cap1"]))
    found = hub.search(capability="cap1")
    assert len(found) == 1


def test_compatibility() -> None:
    hub = EcosystemHub()
    e = _entry("ext", "1.2.0", ["cap1"])
    assert hub.is_compatible(e, "1.0.0") is True


def test_install_via_plugin_runtime() -> None:
    hub = EcosystemHub()
    rt = PluginRuntime()
    e = hub.publish(_entry("ext", "1.0.0", ["cap1"]))
    hub.install(e.entry_id, rt)
    assert rt.get_plugin(e.entry_id) is not None
