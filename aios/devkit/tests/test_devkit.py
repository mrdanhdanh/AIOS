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
