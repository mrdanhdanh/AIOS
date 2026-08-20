"""Architecture tests for Workflow (TASK-008) — AC-008-05 isolation."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path


def test_workflow_package_no_module_load_langgraph():
    workflow_dir = Path(__file__).resolve().parents[1] / "workflow"
    for py in workflow_dir.glob("*.py"):
        source = py.read_text(encoding="utf-8")
        # Only compiler.py may import langgraph; definition/validation just mention it as forbidden key string
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "langgraph", f"{py.name} has top-level import langgraph"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("langgraph"), f"{py.name} has top-level from langgraph"


def test_import_workflow_without_langgraph_installed():
    for mod in list(sys.modules.keys()):
        if mod.startswith("aios.runtime.workflow"):
            del sys.modules[mod]
    mod = importlib.import_module("aios.runtime.workflow")
    assert hasattr(mod, "WorkflowDefinition")
    assert hasattr(mod, "MockCompiler")
    assert hasattr(mod, "LangGraphCompiler")


def test_langgraph_compiler_lazy_flag():
    from aios.runtime.workflow import LangGraphCompiler, WorkflowDefinition

    wd = WorkflowDefinition.from_yaml("workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n")
    cw = LangGraphCompiler().compile(wd)
    assert "langgraph_available" in cw.representation
    assert isinstance(cw.representation["langgraph_available"], bool)
    assert "langgraph_available" in cw.metadata


def test_compiled_representation_engine_tagged():
    from aios.runtime.workflow import LangGraphCompiler, MockCompiler, WorkflowDefinition

    wd = WorkflowDefinition.from_yaml("workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n")
    cw_mock = MockCompiler().compile(wd)
    cw_lg = LangGraphCompiler().compile(wd)
    assert cw_mock.representation["engine"] == "mock"
    assert cw_lg.representation["engine"] == "langgraph"
    assert cw_mock.engine == "mock"
    assert cw_lg.engine == "langgraph"


def test_workflow_definition_no_engine_keys_in_dict():
    from aios.runtime.workflow import WorkflowDefinition

    wd = WorkflowDefinition.from_yaml("workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n")
    d = wd.to_dict()
    wf = d["workflow"]
    for forbidden in ("engine", "langgraph", "engine_config"):
        assert forbidden not in wf
        for node in wf.get("nodes", []):
            assert forbidden not in node
