"""PluginRuntime."""
from __future__ import annotations

from aios.plugin_runtime.contracts import PluginSpec, PluginState
from aios.plugin_runtime.manifest import PluginManifest
from aios.plugin_runtime.resolver import PluginResolver


class PluginRuntime:
    def __init__(self, runtime_version: str = "1.0.0") -> None:
        self._plugins: dict[str, PluginSpec] = {}
        self._manifests: dict[str, PluginManifest] = {}
        self._resolver = PluginResolver(runtime_version)
        self._snapshots: dict[str, PluginState] = {}

    def register(self, spec: PluginSpec) -> PluginSpec:
        self._plugins[spec.plugin_id] = spec
        return spec

    def register_manifest(self, manifest: PluginManifest) -> PluginSpec:
        """Register from a manifest after validation + dependency resolution."""
        errors = manifest.validate()
        if errors:
            raise ValueError(f"Manifest invalid: {errors}")
        self._manifests[manifest.plugin_id] = manifest
        spec = manifest.to_spec()
        self._plugins[spec.plugin_id] = spec
        return spec

    def load(self, pid: str) -> PluginSpec:
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        # Validate manifest before load (fail-closed).
        manifest = self._manifests.get(pid)
        if manifest is not None:
            self._resolver.resolve(manifest, self._manifests)
        self._snapshots[pid] = p.state
        p.state = PluginState.LOADED
        return p

    def enable(self, pid: str) -> PluginSpec:
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        p.state = PluginState.ENABLED
        return p

    def disable(self, pid: str) -> PluginSpec:
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        p.state = PluginState.DISABLED
        return p

    def rollback(self, pid: str) -> PluginSpec:
        """Roll back a plugin to its pre-load state (evidence of prior state)."""
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        prev = self._snapshots.get(pid, PluginState.REGISTERED)
        p.state = prev
        return p

    def list_plugins(self) -> list[PluginSpec]: return list(self._plugins.values())
    def get_plugin(self, pid: str) -> PluginSpec | None: return self._plugins.get(pid)
