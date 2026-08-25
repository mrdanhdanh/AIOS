"""Tests for Workflow Definition + Compiler + Simulation (TASK-008)."""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from aios.runtime.workflow import (
    CompiledWorkflow,
    LangGraphCompiler,
    MockCompiler,
    WorkflowDefinition,
    WorkflowError,
    simulate,
    simulate_yaml,
)
from aios.runtime.workflow.contracts import WORKFLOW_CONTRACT, check_workflow_contract

VALID_YAML = """
workflow:
  name: review_project
  version: "1.0.0"
  description: Review project source code
  nodes:
    - id: analyze
      type: task
      capability: analyze_code
    - id: test
      type: task
      capability: run_tests
    - id: report
      type: task
      capability: generate_report
  edges:
    - from: analyze
      to: test
    - from: test
      to: report
  retries: 2
  timeout: 300
  resources:
    cpu: 2
    memory: 2GB
  permissions:
    - filesystem.read
    - process.execute
"""

MINIMAL_YAML = """
workflow:
  name: minimal
  version: "0.1.0"
  nodes:
    - id: a
      type: task
  edges: []
"""


def test_valid_yaml_parses_and_roundtrips():
    wd = WorkflowDefinition.from_yaml(VALID_YAML)
    assert wd.name == "review_project"
    assert wd.version == "1.0.0"
    assert len(wd.nodes) == 3
    assert len(wd.edges) == 2
    yaml2 = wd.to_yaml()
    wd2 = WorkflowDefinition.from_yaml(yaml2)
    assert wd2.name == wd.name
    assert [n.id for n in wd2.nodes] == [n.id for n in wd.nodes]


def test_minimal_yaml():
    wd = WorkflowDefinition.from_yaml(MINIMAL_YAML)
    assert wd.name == "minimal"
    wd.validate()


def test_from_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        wd = WorkflowDefinition.from_file(path)
        assert wd.name == "review_project"
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def test_content_hash_deterministic():
    wd = WorkflowDefinition.from_yaml(VALID_YAML)
    assert wd.content_hash() == wd.content_hash()
    wd2 = WorkflowDefinition.from_yaml(VALID_YAML)
    assert wd.content_hash() == wd2.content_hash()


def test_to_artifact():
    wd = WorkflowDefinition.from_yaml(VALID_YAML)
    art = wd.to_artifact()
    assert art.name == "review_project"
    assert art.version == "1.0.0"
    assert art.content_type == "application/yaml"


def test_missing_name_rejects():
    with pytest.raises(WorkflowError, match="workflow.name"):
        WorkflowDefinition.from_yaml("workflow:\n  version: '1.0.0'\n  nodes: []\n")


def test_missing_version_rejects():
    with pytest.raises(WorkflowError, match="workflow.version"):
        WorkflowDefinition.from_yaml("workflow:\n  name: x\n  nodes: []\n")


def test_invalid_semver_rejects():
    with pytest.raises(WorkflowError, match="SemVer"):
        WorkflowDefinition.from_yaml("workflow:\n  name: x\n  version: 'bad'\n  nodes: []\n")


def test_missing_node_id_rejects():
    with pytest.raises(WorkflowError, match="node missing.*id|node.id"):
        WorkflowDefinition.from_yaml("workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - type: task\n")


def test_duplicate_node_id_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n    - id: a\n"
    with pytest.raises(WorkflowError, match="duplicate node"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_edge_to_unknown_node_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n  edges:\n    - from: a\n      to: missing\n"
    with pytest.raises(WorkflowError, match="unknown node"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_duplicate_edge_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n    - id: b\n  edges:\n    - from: a\n      to: b\n    - from: a\n      to: b\n"
    with pytest.raises(WorkflowError, match="duplicate edge"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_self_loop_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n  edges:\n    - from: a\n      to: a\n"
    with pytest.raises(WorkflowError, match="self-loop"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_cycle_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n    - id: b\n    - id: c\n  edges:\n    - from: a\n      to: b\n    - from: b\n      to: c\n    - from: c\n      to: a\n"
    with pytest.raises(WorkflowError, match="cycle"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_unsupported_permission_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes: []\n  permissions: ['filesystem.read', 'bad.perm']\n"
    with pytest.raises(WorkflowError, match="not allowed"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_invalid_resource_rejects():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes: []\n  resources:\n    cpu: 0\n    memory: 2GB\n"
    with pytest.raises(WorkflowError, match="cpu"):
        WorkflowDefinition.from_yaml(yaml_text)
    yaml_text2 = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes: []\n  resources:\n    cpu: 1\n    memory: bad\n"
    with pytest.raises(WorkflowError, match="memory"):
        WorkflowDefinition.from_yaml(yaml_text2)


def test_invalid_retries_timeout_rejects():
    wd = WorkflowDefinition(name="x", version="1.0.0", retries=-1, timeout=300)
    with pytest.raises(WorkflowError):
        wd.validate()
    wd2 = WorkflowDefinition(name="x", version="1.0.0", retries=0, timeout=0)
    with pytest.raises(WorkflowError):
        wd2.validate()


def test_engine_key_rejected():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  engine: langgraph\n  nodes: []\n"
    with pytest.raises(WorkflowError, match="forbidden.*engine"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_node_engine_key_rejected():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: a\n      engine: langgraph\n"
    with pytest.raises(WorkflowError, match="forbidden"):
        WorkflowDefinition.from_yaml(yaml_text)


def test_invalid_yaml_rejects():
    with pytest.raises(WorkflowError, match="invalid YAML"):
        WorkflowDefinition.from_yaml("::: not yaml :::\n  - [\n")


def test_mock_compiler_produces_compiled():
    wd = WorkflowDefinition.from_yaml(VALID_YAML)
    cw = MockCompiler().compile(wd)
    assert isinstance(cw, CompiledWorkflow)
    assert cw.engine == "mock"
    assert cw.workflow.name == wd.name
    assert cw.representation["topo_order"] == ["analyze", "test", "report"]


def test_langgraph_compiler_produces_compiled():
    wd = WorkflowDefinition.from_yaml(VALID_YAML)
    cw = LangGraphCompiler().compile(wd)
    assert cw.engine == "langgraph"
    assert cw.workflow.name == wd.name
    assert "langgraph_available" in cw.representation


def test_both_compilers_same_definition():
    wd = WorkflowDefinition.from_yaml(VALID_YAML)
    cw1 = MockCompiler().compile(wd)
    cw2 = LangGraphCompiler().compile(wd)
    assert cw1.workflow.name == cw2.workflow.name
    assert cw1.workflow.version == cw2.workflow.version
    assert wd.name == "review_project"


def test_compiler_rejects_invalid():
    from aios.runtime.workflow.definition import WorkflowEdge

    wd2 = WorkflowDefinition(name="x", version="1.0.0", nodes=[], edges=[WorkflowEdge(from_id="a", to_id="b")])
    with pytest.raises(WorkflowError):
        MockCompiler().compile(wd2)
    with pytest.raises(WorkflowError):
        LangGraphCompiler().compile(wd2)


def test_mock_compiler_topo_deterministic():
    yaml_text = "workflow:\n  name: x\n  version: '1.0.0'\n  nodes:\n    - id: c\n    - id: a\n    - id: b\n  edges:\n    - from: a\n      to: c\n"
    wd = WorkflowDefinition.from_yaml(yaml_text)
    cw1 = MockCompiler().compile(wd)
    cw2 = MockCompiler().compile(wd)
    assert cw1.representation["topo_order"] == cw2.representation["topo_order"]
    assert cw1.representation["topo_order"].index("a") < cw1.representation["topo_order"].index("c")


def test_simulate_yaml_success():
    result = simulate_yaml(VALID_YAML)
    assert result.success is True
    assert result.llm_calls == 0
    assert result.tool_calls == 0
    assert len(result.node_results) == 3
    assert all(r.status == "SUCCEEDED" for r in result.node_results)
    assert result.compiled.representation["topo_order"] == ["analyze", "test", "report"]


def test_simulate_invalid_returns_fail():
    result = simulate_yaml("workflow:\n  name: x\n  version: bad\n")
    assert result.success is False
    assert result.error is not None
    assert result.llm_calls == 0
    assert result.tool_calls == 0


def test_simulate_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        result = simulate(path)
        assert result.success is True
        assert result.llm_calls == 0
        assert result.tool_calls == 0
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def test_simulate_deterministic():
    r1 = simulate_yaml(VALID_YAML)
    r2 = simulate_yaml(VALID_YAML)
    assert [n.node_id for n in r1.node_results] == [n.node_id for n in r2.node_results]
    assert r1.compiled.representation["topo_order"] == r2.compiled.representation["topo_order"]


def test_simulate_events_present():
    result = simulate_yaml(VALID_YAML)
    assert any(e["type"] == "workflow.started" for e in result.events)
    assert any(e["type"] == "workflow.completed" for e in result.events)
    assert any(e["type"] == "node.started" for e in result.events)


def test_check_workflow_contract_pass():
    check_workflow_contract("1.0.0")
    check_workflow_contract("1.9.9")


# --------------------------------------------------------------------------- #
# TASK-228 — Unified ExecutionPlan Contract
# --------------------------------------------------------------------------- #
def test_to_execution_plan_carries_governance_fields():
    yaml_text = (
        "workflow:\n"
        "  name: exec-demo\n"
        "  version: '1.0.0'\n"
        "  permissions: [process.execute]\n"
        "  nodes:\n"
        "    - id: step-1\n"
        "      type: task\n"
        "      command: echo hello\n"
        "    - id: step-2\n"
        "      type: task\n"
        "      command: git status\n"
    )
    wf = WorkflowDefinition.from_yaml(yaml_text)
    plan = wf.to_execution_plan(allowed_cwd="/tmp/work")
    assert plan.metadata["contract"] == "unified-execution-plan"
    assert plan.metadata["policy_ref"] == "governance.unified-gate"
    assert plan.metadata["permissions"] == ["process.execute"]
    assert len(plan.steps) == 2
    s1 = plan.get_step("step-1")
    assert s1.metadata["permission"] == "process.execute"
    assert s1.metadata["evidence_ref"] == "evidence:step-1"
    assert s1.metadata["cwd"] == "/tmp/work"
    s2 = plan.get_step("step-2")
    assert s2.metadata["tool_type"] == "git"


def test_execution_plan_round_trip_lossless():
    yaml_text = (
        "workflow:\n"
        "  name: roundtrip\n"
        "  version: '2.3.4'\n"
        "  permissions: [process.execute]\n"
        "  nodes:\n"
        "    - id: a\n"
        "      type: task\n"
        "      command: echo a\n"
        "    - id: b\n"
        "      type: task\n"
        "      command: echo b\n"
    )
    wf = WorkflowDefinition.from_yaml(yaml_text)
    plan = wf.to_execution_plan(allowed_cwd="/tmp/rt")
    back = WorkflowDefinition.from_execution_plan(plan)
    assert back.name == "roundtrip"
    assert back.version == "2.3.4"
    assert back.permissions == ["process.execute"]
    assert len(back.nodes) == 2
    assert back.nodes[0].id == "a"
    assert back.nodes[0].command == "echo a"
    assert back.nodes[1].id == "b"
    # Re-convert and compare step ids/commands (lossless for controlled fields).
    plan2 = back.to_execution_plan(allowed_cwd="/tmp/rt")
    assert [s.step_id for s in plan2.steps] == ["a", "b"]
    assert [s.metadata["command"] for s in plan2.steps] == ["echo a", "echo b"]


def test_check_workflow_contract_reject():
    from aios.core.contracts import ContractError

    with pytest.raises(ContractError):
        check_workflow_contract("0.9.0")
    with pytest.raises(ContractError):
        check_workflow_contract("2.0.0")


def test_workflow_contract_object():
    assert WORKFLOW_CONTRACT.name == "runtime.workflow"
    assert ">=1.0.0" in WORKFLOW_CONTRACT.version_range


def test_cli_validate_valid():
    from aios.cli.workflow_cli import main

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        rc = main(["validate", path])
        assert rc == 0
        rc2 = main(["workflow", "validate", path])
        assert rc2 == 0
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def test_cli_validate_invalid():
    from aios.cli.workflow_cli import main

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write("workflow:\n  name: x\n  version: bad\n")
        path = f.name
    try:
        rc = main(["validate", path])
        assert rc == 1
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def test_cli_run_simulate_success():
    from aios.cli.workflow_cli import main

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        rc = main(["run", path, "--simulate"])
        assert rc == 0
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def test_cli_run_without_simulate_returns_2():
    from aios.cli.workflow_cli import main

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        rc = main(["run", path])
        assert rc == 2
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def test_cli_run_missing_file():
    from aios.cli.workflow_cli import main

    rc = main(["run", "/tmp/__no_such_workflow_aios_test.yaml", "--simulate"])
    assert rc in (1, 2)


def test_cli_run_simulate_json():
    from aios.cli.workflow_cli import main
    import io
    from contextlib import redirect_stdout
    import json

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["run", path, "--simulate", "--json"])
        assert rc == 0
        data = json.loads(buf.getvalue())
        assert data["success"] is True
        assert data["llm_calls"] == 0
        assert data["tool_calls"] == 0
    finally:
        pathlib.Path(path).unlink(missing_ok=True)
