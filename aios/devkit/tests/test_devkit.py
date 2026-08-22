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


class TestT071Scaffold:
    def test_scaffold_capability(self):
        from aios.devkit.scaffold import DevKitScaffold
        dk = DevKitScaffold()
        art = dk.scaffold_artifact("capability", "mycap")
        assert art.kind == "capability"
        assert any(f.path.endswith("aios/capability/mycap.py") for f in art.files)
        result = dk.verify_conformance(art)
        assert result["passed"] is True
        assert result["architecture"]["passed"] is True
        assert result["contract"]["valid"] is True
        assert result["boundary"]["valid"] is True

    def test_scaffold_agent_tool_workflow(self):
        from aios.devkit.scaffold import DevKitScaffold
        dk = DevKitScaffold()
        for kind in ("agent", "tool", "workflow"):
            art = dk.scaffold_artifact(kind, f"my{kind}")
            res = dk.verify_conformance(art)
            assert res["passed"] is True, kind

    def test_scaffold_deterministic(self):
        from aios.devkit.scaffold import DevKitScaffold
        dk = DevKitScaffold()
        a1 = dk.scaffold_artifact("capability", "cap", "1.0.0")
        a2 = dk.scaffold_artifact("capability", "cap", "1.0.0")
        assert [f.code for f in a1.files] == [f.code for f in a2.files]
        assert a1.spec["spec_id"] == a2.spec["spec_id"]

    def test_scaffold_unknown_kind(self):
        from aios.devkit.errors import ActionableError
        from aios.devkit.scaffold import DevKitScaffold
        dk = DevKitScaffold()
        try:
            dk.scaffold_artifact("bogus", "x")
            assert False, "expected ActionableError"
        except ActionableError as exc:
            assert "cause" in exc.to_dict()

    def test_render_writes_files(self, tmp_path):
        from aios.devkit.scaffold import DevKitScaffold
        dk = DevKitScaffold()
        art = dk.scaffold_artifact("capability", "rendered")
        written = dk.render(art, str(tmp_path))
        assert len(written) == len(art.files)
        assert (tmp_path / "aios" / "capability" / "rendered.py").exists()


class TestT071Cli:
    def test_cli_scaffold_verify(self):
        from aios.devkit.cli import DevKitCLI
        cli = DevKitCLI()
        art = cli.scaffold("capability", "dxcap")
        assert art["conforms_to"]["architecture"] == "1.0"
        res = cli.verify(art)
        assert res["passed"] is True

    def test_actionable_error_format(self):
        from aios.devkit.errors import ActionableError, format_actionable
        err = ActionableError("boom", cause="c", fix_hint="f")
        out = format_actionable(err)
        assert "cause: c" in out and "fix: f" in out

    def test_wrap_error_preserves_original(self):
        from aios.devkit.errors import wrap_error
        wrapped = wrap_error(ValueError("bad"), cause="c", fix_hint="f")
        assert "ValueError" in str(wrapped)
        assert wrapped.cause == "c"


class TestT071CliVersionPolicy:
    def test_breaking_without_bump_raises(self):
        from aios.devkit.cli_version import CliVersionPolicy
        from aios.devkit.errors import CliVersionBumpRequired
        policy = CliVersionPolicy(current_version="1.0.0")
        try:
            policy.assert_stable(["run", "validate"], ["run"], "1.0.0")
            assert False, "expected CliVersionBumpRequired"
        except CliVersionBumpRequired:
            pass

    def test_breaking_with_bump_passes(self):
        from aios.devkit.cli_version import CliVersionPolicy
        policy = CliVersionPolicy(current_version="2.0.0")
        removed = policy.assert_stable(["run", "validate"], ["run"], "1.0.0")
        assert removed == ["validate"]

    def test_no_breaking_is_stable(self):
        from aios.devkit.cli_version import CliVersionPolicy
        policy = CliVersionPolicy(current_version="1.0.0")
        assert policy.assert_stable(["run", "validate"], ["run", "validate"]) == []

    def test_deprecate_records_window(self):
        from aios.devkit.cli_version import CliVersionPolicy
        rec = CliVersionPolicy().deprecate("oldcmd", "1.0.0", "2.0.0")
        assert rec["status"] == "deprecated"
        assert rec["remove_in"] == "2.0.0"
