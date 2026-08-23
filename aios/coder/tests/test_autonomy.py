"""Unit + Contract + Integration + Architecture + Regression tests (TASK-132)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.autonomy import (
    AutonomyLevel,
    AutonomyPermissionBroker,
    PermissionError_ as CoderPermissionError,
)


# --------------------------------------------------------------------------- #
# Level -> permission mapping
# --------------------------------------------------------------------------- #
def test_supervised_cannot_apply():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.SUPERVISED)
    assert b.check("plan").allowed is True
    assert b.check("review").allowed is True
    assert b.check("apply").allowed is False
    assert b.check("patch").allowed is False


def test_assisted_can_generate_not_apply():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.ASSISTED)
    assert b.check("generate").allowed is True
    assert b.check("apply").allowed is False


def test_autonomous_can_apply_and_patch():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.AUTONOMOUS)
    assert b.check("apply").allowed is True
    assert b.check("patch").allowed is True


# --------------------------------------------------------------------------- #
# Fail-closed
# --------------------------------------------------------------------------- #
def test_require_raises_on_denial():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.SUPERVISED)
    with pytest.raises(CoderPermissionError):
        b.require("apply")


def test_policy_rejected():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.AUTONOMOUS)
    d = b.check("apply", policy_ok=False)
    assert d.allowed is False


def test_unknown_operation_denied():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.AUTONOMOUS)
    assert b.check("delete-everything").allowed is False


def test_agent_id_required():
    with pytest.raises(CoderPermissionError):
        AutonomyPermissionBroker("", AutonomyLevel.AUTONOMOUS)


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_decision_has_evidence():
    b = AutonomyPermissionBroker("coder-1", AutonomyLevel.AUTONOMOUS)
    d = b.check("apply")
    assert d.evidence_id.startswith("ev-")
    assert len(d.content_hash) == 64


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "autonomy.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    forbidden = {"subprocess", "os", "aios.runtime.providers", "aios.runtime.filesystem"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not (imported & forbidden), f"forbidden imports: {imported & forbidden}"
