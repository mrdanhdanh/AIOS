"""PluginRuntime."""
from __future__ import annotations
from aios.plugin_runtime.contracts import PluginSpec, PluginState

class PluginRuntime:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginSpec] = {}
    def register(self, spec: PluginSpec) -> PluginSpec:
        self._plugins[spec.plugin_id] = spec; return spec
    def load(self, pid: str) -> PluginSpec:
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        p.state = PluginState.LOADED; return p
    def enable(self, pid: str) -> PluginSpec:
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        p.state = PluginState.ENABLED; return p
    def disable(self, pid: str) -> PluginSpec:
        p = self._plugins.get(pid)
        if p is None: raise RuntimeError(f"Plugin {pid!r} not found")
        p.state = PluginState.DISABLED; return p
    def list_plugins(self) -> list[PluginSpec]: return list(self._plugins.values())
    def get_plugin(self, pid: str) -> PluginSpec | None: return self._plugins.get(pid)
