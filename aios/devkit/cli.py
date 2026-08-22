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

    # --- T071: DevArtifact scaffolding + conformance -------------------------

    def scaffold(
        self,
        kind: str,
        name: str,
        version: str = "1.0.0",
        author: str = "",
    ) -> dict:
        """Generate a capability/agent/tool/workflow skeleton (T071 DX)."""
        artifact = self._scaffold.scaffold_artifact(kind, name, version, author)
        return artifact.to_dict()

    def verify(self, artifact_dict: dict) -> dict:
        """Verify a scaffolded artifact against T063 + T064 (T071 DX)."""
        from aios.devkit.scaffold import GeneratedFile, ScaffoldArtifact
        artifact = ScaffoldArtifact(
            kind=artifact_dict.get("kind", ""),
            name=artifact_dict.get("name", ""),
            version=artifact_dict.get("version", ""),
            author=artifact_dict.get("author", ""),
            template_version=artifact_dict.get("template_version", ""),
            spec=artifact_dict.get("spec", {}),
            files=[
                GeneratedFile(path=f.get("path", ""), code=f.get("code", ""), module_path=f.get("module_path", ""))
                for f in artifact_dict.get("files", [])
            ],
        )
        return self._scaffold.verify_conformance(artifact)
