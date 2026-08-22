"""EcosystemHub."""
from __future__ import annotations

import hashlib

from aios.ecosystem_hub.contracts import HubEntry, HubStatus


def _parse_version(version: str) -> tuple[int, int, int]:
    nums = [int(p.split("-")[0]) for p in version.split(".")[:3]]
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


class EcosystemHub:
    def __init__(self) -> None:
        self._entries: dict[str, HubEntry] = {}

    def publish(self, entry: HubEntry) -> HubEntry:
        payload = f"{entry.name}|{entry.version}|{entry.capabilities}"
        entry.checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        entry.provenance.append(f"hub:publish:{entry.checksum}")
        entry.status = HubStatus.PUBLISHED
        self._entries[entry.entry_id] = entry
        return entry

    def unpublish(self, eid: str) -> HubEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.status = HubStatus.UNPUBLISHED
        return e

    def download(self, eid: str) -> HubEntry | None:
        e = self._entries.get(eid)
        if e: e.downloads += 1
        return e

    def list_entries(self) -> list[HubEntry]: return list(self._entries.values())
    def get_entry(self, eid: str) -> HubEntry | None: return self._entries.get(eid)

    # --- Discovery / search / compatibility ---
    def search(self, query: str = "", capability: str = "") -> list[HubEntry]:
        results: list[HubEntry] = []
        for e in self._entries.values():
            if e.status != HubStatus.PUBLISHED:
                continue
            if query and query.lower() not in e.name.lower():
                continue
            if capability and capability not in e.capabilities:
                continue
            results.append(e)
        return results

    def is_compatible(self, entry: HubEntry, contract_version: str = "1.0.0") -> bool:
        em, emi, _ = _parse_version(entry.version)
        cm, cmi, _ = _parse_version(contract_version)
        return em == cm and emi >= cmi

    def install(self, eid: str, runtime: "object | None" = None) -> HubEntry:
        """Install a published entry via the Plugin Runtime (if provided)."""
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        if e.status != HubStatus.PUBLISHED:
            raise RuntimeError(f"Entry {eid!r} is not published")
        if runtime is not None:
            from aios.plugin_runtime.manifest import PluginManifest
            manifest = PluginManifest(
                plugin_id=e.entry_id,
                name=e.name,
                version=e.version,
                capabilities=list(e.capabilities),
            )
            runtime.register_manifest(manifest)
        e.provenance.append(f"hub:install:{e.entry_id}")
        return e
