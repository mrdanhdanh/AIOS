"""EcosystemHub."""
from __future__ import annotations
from aios.ecosystem_hub.contracts import HubEntry, HubStatus

class EcosystemHub:
    def __init__(self) -> None:
        self._entries: dict[str, HubEntry] = {}
    def publish(self, entry: HubEntry) -> HubEntry:
        entry.status = HubStatus.PUBLISHED
        self._entries[entry.entry_id] = entry
        return entry
    def unpublish(self, eid: str) -> HubEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.status = HubStatus.UNPUBLISHED; return e
    def download(self, eid: str) -> HubEntry | None:
        e = self._entries.get(eid)
        if e: e.downloads += 1
        return e
    def list_entries(self) -> list[HubEntry]: return list(self._entries.values())
    def get_entry(self, eid: str) -> HubEntry | None: return self._entries.get(eid)
