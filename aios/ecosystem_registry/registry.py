"""EcosystemRegistry."""
from __future__ import annotations

import hashlib

from aios.ecosystem_registry.contracts import (
    RegistryEntry,
    RegistryStatus,
    TrustState,
)


def _parse_version(version: str) -> tuple[int, int, int]:
    nums = [int(p.split("-")[0]) for p in version.split(".")[:3]]
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


class EcosystemRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}

    def register(self, entry: RegistryEntry) -> RegistryEntry:
        # Compute a content checksum for integrity/discovery.
        payload = f"{entry.name}|{entry.version}|{entry.entry_type}|{entry.platform}"
        entry.checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self._entries[entry.entry_id] = entry
        return entry

    def approve(self, eid: str) -> RegistryEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.status = RegistryStatus.APPROVED
        return e

    def reject(self, eid: str) -> RegistryEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.status = RegistryStatus.REJECTED
        return e

    def set_trust(self, eid: str, trust: TrustState) -> RegistryEntry:
        e = self._entries.get(eid)
        if e is None: raise RuntimeError(f"Entry {eid!r} not found")
        e.trust = trust
        return e

    def list_entries(self, status: RegistryStatus | None = None) -> list[RegistryEntry]:
        entries = list(self._entries.values())
        if status: entries = [e for e in entries if e.status == status]
        return entries

    def get_entry(self, eid: str) -> RegistryEntry | None: return self._entries.get(eid)

    # --- Discovery / search / resolution ---
    def search(self, query: str = "", capability: str = "", entry_type: str = "",
               platform: str = "", trust: TrustState | None = None) -> list[RegistryEntry]:
        results: list[RegistryEntry] = []
        for e in self._entries.values():
            if query and query.lower() not in e.name.lower():
                continue
            if capability and capability not in e.capabilities:
                continue
            if entry_type and e.entry_type != entry_type:
                continue
            if platform and platform != "any" and e.platform not in ("any", platform):
                continue
            if trust is not None and e.trust != trust:
                continue
            results.append(e)
        return results

    def resolve_version(self, name: str, contract_version: str = "1.0.0") -> RegistryEntry | None:
        """Resolve the latest compatible approved+certified entry by name."""
        cm, cmi, _ = _parse_version(contract_version)
        candidates = [
            e for e in self._entries.values()
            if e.name == name
            and e.status == RegistryStatus.APPROVED
            and e.trust == TrustState.CERTIFIED
        ]
        compatible = []
        for e in candidates:
            em, emi, _ = _parse_version(e.version)
            if em == cm and emi >= cmi:
                compatible.append(e)
        if not compatible:
            return None
        return max(compatible, key=lambda e: _parse_version(e.version))

    def is_compatible(self, entry: RegistryEntry, contract_version: str = "1.0.0") -> bool:
        em, emi, _ = _parse_version(entry.version)
        cm, cmi, _ = _parse_version(contract_version)
        return em == cm and emi >= cmi
