"""DevKit CLI — method-based command surface (create/validate/test/simulate/package/inspect)."""

from __future__ import annotations

from aios.devkit.manifest import DevKitManifest
from aios.devkit.packaging import Packager
from aios.devkit.scaffold import DevKitScaffold


class DevKitCLI:
    """Command surface mirroring `aios dev <command>` (no external deps)."""

    def __init__(self) -> None:
        self._scaffold = DevKitScaffold()
        self._packager = Packager()

    def create(self, project_name: str, template: str = "default") -> dict:
        from aios.devkit.contracts import ScaffoldConfig
        return self._scaffold.scaffold(ScaffoldConfig(project_name=project_name, template=template))

    def validate(self, manifest: DevKitManifest) -> dict:
        errors = manifest.validate()
        return {"valid": not errors, "errors": errors}

    def test(self, manifest: DevKitManifest) -> dict:
        """Run a local contract-compat check (deterministic, no LLM)."""
        return {"passed": not manifest.validate()}

    def simulate(self, manifest: DevKitManifest) -> dict:
        """Simulate harness execution (offline, deterministic)."""
        return {"simulated": True, "name": manifest.name, "capabilities": manifest.capabilities}

    def package(self, manifest: DevKitManifest, files: list[str]) -> dict:
        return self._packager.package(manifest, files)

    def inspect(self, project_name: str, template: str = "default") -> dict:
        result = self.create(project_name, template)
        result["inspected"] = True
        return result
