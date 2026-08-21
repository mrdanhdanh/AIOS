"""EcosystemRegistry."""
from __future__ import annotations
from aios.ecosystem_registry.contracts import RegistryEntry, RegistryStatus

class EcosystemRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}
    def register(self, entry: RegistryEntry) -> RegistryEntry:
        self._entries[entry.entry_id] = entry; return entry
    def approve(self, eid: str) -> RegistryEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.status = RegistryStatus.APPROVED; return e
    def reject(self, eid: str) -> RegistryEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.status = RegistryStatus.REJECTED; return e
    def list_entries(self, status: RegistryStatus | None = None) -> list[RegistryEntry]:
        entries = list(self._entries.values())
        if status: entries = [e for e in entries if e.status == status]
        return entries
    def get_entry(self, eid: str) -> RegistryEntry | None: return self._entries.get(eid)
