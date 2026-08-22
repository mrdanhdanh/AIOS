"""Harness Registry — register/lookup harness specs by id + version (AC-029-02)."""

from __future__ import annotations

from aios.harness.contracts import HarnessSpec


class HarnessRegistry:
    """Registry of harness specs, keyed by (spec_id, version)."""

    def __init__(self) -> None:
        self._specs: dict[tuple[str, str], HarnessSpec] = {}

    def register(self, spec: HarnessSpec) -> HarnessSpec:
        key = (spec.spec_id, spec.version)
        if key in self._specs:
            raise ValueError(f"Duplicate harness spec: {spec.spec_id} v{spec.version}")
        self._specs[key] = spec
        return spec

    def get(self, spec_id: str, version: str) -> HarnessSpec | None:
        return self._specs.get((spec_id, version))

    def get_latest(self, spec_id: str) -> HarnessSpec | None:
        matches = [s for (sid, _), s in self._specs.items() if sid == spec_id]
        if not matches:
            return None
        return max(matches, key=lambda s: [int(p) for p in s.version.split(".")])

    def list_specs(self) -> list[HarnessSpec]:
        return list(self._specs.values())

    def unregister(self, spec_id: str, version: str) -> None:
        self._specs.pop((spec_id, version), None)
