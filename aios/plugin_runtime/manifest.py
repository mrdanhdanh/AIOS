"""Plugin manifest — schema + validation (fail-closed before load)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.plugin_runtime.contracts import PluginSpec, PluginState


@dataclass
class PluginManifest:
    """Declarative plugin manifest (validated before load)."""
    plugin_id: str = ""
    name: str = ""
    version: str = "1.0.0"
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    min_runtime_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "min_runtime_version": self.min_runtime_version,
        }

    def validate(self) -> list[str]:
        """Return a list of validation errors (empty = valid)."""
        errors: list[str] = []
        if not self.plugin_id:
            errors.append("plugin_id is required")
        if not self.name:
            errors.append("name is required")
        if not isinstance(self.version, str) or not self.version:
            errors.append("version must be a non-empty string")
        if not isinstance(self.capabilities, list):
            errors.append("capabilities must be a list")
        if not isinstance(self.dependencies, list):
            errors.append("dependencies must be a list")
        return errors

    def to_spec(self) -> PluginSpec:
        return PluginSpec(
            plugin_id=self.plugin_id,
            name=self.name,
            version=self.version,
            state=PluginState.REGISTERED,
            capabilities=list(self.capabilities),
        )
