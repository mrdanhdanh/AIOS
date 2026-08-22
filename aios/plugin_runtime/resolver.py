"""Plugin dependency + compatibility resolver."""

from __future__ import annotations

from aios.plugin_runtime.manifest import PluginManifest


class PluginResolver:
    """Resolves plugin dependencies and checks compatibility (fail-closed)."""

    def __init__(self, runtime_version: str = "1.0.0") -> None:
        self._runtime_version = runtime_version

    def resolve(self, manifest: PluginManifest, registry: dict[str, PluginManifest]) -> list[str]:
        """Return ordered dependency ids; raises if unresolvable/incompatible."""
        errors = manifest.validate()
        if errors:
            raise ValueError(f"Manifest invalid: {errors}")
        if self._runtime_version < manifest.min_runtime_version:
            raise ValueError(
                f"Runtime {self._runtime_version} < required {manifest.min_runtime_version}"
            )
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(pid: str) -> None:
            if pid in visited:
                return
            dep = registry.get(pid)
            if dep is None:
                raise ValueError(f"Missing dependency: {pid}")
            visited.add(pid)
            for d in dep.dependencies:
                visit(d)
            ordered.append(pid)

        visit(manifest.plugin_id)
        return ordered
