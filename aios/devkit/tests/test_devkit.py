"""Tests for devkit."""
from __future__ import annotations
from aios.devkit.contracts import ProjectTemplate, ScaffoldConfig
from aios.devkit.scaffold import DevKitScaffold

class TestDevKit:
    def test_register_template(self):
        dk = DevKitScaffold()
        dk.register_template(ProjectTemplate(name="python", files=["main.py", "tests/"]))
        assert len(dk.list_templates()) == 1
    def test_scaffold(self):
        dk = DevKitScaffold()
        dk.register_template(ProjectTemplate(name="python", files=["main.py"]))
        result = dk.scaffold(ScaffoldConfig(project_name="myapp", template="python"))
        assert result["status"] == "created"
        assert result["project"] == "myapp"
    def test_scaffold_default(self):
        dk = DevKitScaffold()
        result = dk.scaffold(ScaffoldConfig(project_name="test"))
        assert result["status"] == "created"
    def test_get_template(self):
        dk = DevKitScaffold()
        dk.register_template(ProjectTemplate(name="web"))
        assert dk.get_template("web") is not None
        assert dk.get_template("nonexistent") is None
    def test_to_dict(self):
        t = ProjectTemplate(name="api", files=["app.py"])
        d = t.to_dict()
        assert d["name"] == "api"


class TestDevKitT047:
    def test_manifest_validation(self):
        from aios.devkit.manifest import DevKitManifest
        assert DevKitManifest(name="", version="", entrypoint="").validate()
        assert DevKitManifest(name="x", version="1.0.0", entrypoint="main.py").validate() == []

    def test_packaging_checksum(self):
        from aios.devkit.manifest import DevKitManifest
        from aios.devkit.packaging import Packager
        m = DevKitManifest(name="x", version="1.0.0", entrypoint="main.py")
        bundle = Packager().package(m, ["main.py"])
        assert bundle["checksum"] != ""

    def test_cli_create_validate_package(self):
        from aios.devkit.cli import DevKitCLI
        from aios.devkit.manifest import DevKitManifest
        cli = DevKitCLI()
        created = cli.create("proj")
        assert created["project"] == "proj"
        m = DevKitManifest(name="x", version="1.0.0", entrypoint="main.py")
        assert cli.validate(m)["valid"] is True
        assert cli.test(m)["passed"] is True
        assert cli.simulate(m)["simulated"] is True
        bundle = cli.package(m, ["main.py"])
        assert "checksum" in bundle
        assert cli.inspect("proj")["inspected"] is True
