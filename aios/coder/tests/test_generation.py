"""Unit + Contract + Integration + Architecture + Regression tests (TASK-127)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.generation import (
    CodeGenerationRuntime,
    GenerationStatus,
    GeneratedArtifact,
)
from aios.coder.planner import CodingPlan, CodingPlanner, CodingStep, PlanStatus, PlanVerifier


class _FakeCapability:
    """Stand-in for a real Capability (T009/T014). Returns deterministic code."""

    def execute(self, action: str, target: str) -> str:
        return f"# {action} -> {target}\ndef {target.split('/')[-1].split('.')[0]}():\n    pass\n"


def _verified_plan():
    plan = CodingPlanner().plan("add function")
    return PlanVerifier().verify(plan)


# --------------------------------------------------------------------------- #
# Plan execution -> artifacts
# --------------------------------------------------------------------------- #
def test_execute_plan_emits_artifacts():
    rt = CodeGenerationRuntime(_FakeCapability())
    run = rt.run(_verified_plan())
    assert run.status is GenerationStatus.SUCCEEDED
    assert len(run.artifacts) == len(run.steps_executed) > 0


def test_artifact_has_content_hash_and_evidence():
    rt = CodeGenerationRuntime(_FakeCapability())
    run = rt.run(_verified_plan())
    art: GeneratedArtifact = run.artifacts[0]
    assert len(art.content_hash) == 64
    assert art.evidence_id.startswith("ev-")


# --------------------------------------------------------------------------- #
# Fail-closed
# --------------------------------------------------------------------------- #
def test_unverified_plan_rejected():
    plan = CodingPlanner().plan("add function")  # not verified
    rt = CodeGenerationRuntime(_FakeCapability())
    with pytest.raises(Exception):
        rt.run(plan)


def test_unhashable_artifact_rejected():
    class _BadCap:
        def execute(self, action, target):
            return None  # not a string -> unhashable

    rt = CodeGenerationRuntime(_BadCap())
    with pytest.raises(Exception):
        rt.run(_verified_plan())


# --------------------------------------------------------------------------- #
# Deterministic
# --------------------------------------------------------------------------- #
def test_same_plan_same_artifact_set():
    rt = CodeGenerationRuntime(_FakeCapability())
    a = rt.run(_verified_plan())
    b = rt.run(_verified_plan())
    assert [x.content_hash for x in a.artifacts] == [x.content_hash for x in b.artifacts]


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports / no direct tool access
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "generation.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = {"subprocess", "os", "aios.runtime.providers", "aios.runtime.filesystem", "aios.tool"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not (imported & forbidden), f"forbidden imports: {imported & forbidden}"


def test_runtime_uses_capability_not_direct_tool():
    # The runtime must receive a capability, not import a tool module directly.
    rt = CodeGenerationRuntime(_FakeCapability())
    assert hasattr(rt._capability, "execute")
