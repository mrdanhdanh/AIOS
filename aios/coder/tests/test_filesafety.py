"""Unit + Contract + Integration + Architecture + Regression tests (TASK-134)."""

from __future__ import annotations

import ast
import os
import tempfile
from pathlib import Path

import pytest

from aios.coder.filesafety import FileSafetyBoundary, FileSafetyError, ScopeStatus


@pytest.fixture
def boundary():
    root = tempfile.mkdtemp(prefix="coder-scope-")
    return FileSafetyBoundary(root), root


# --------------------------------------------------------------------------- #
# In-scope allowed
# --------------------------------------------------------------------------- #
def test_in_scope_allowed(boundary):
    b, root = boundary
    d = b.check("src/main.py")
    assert d.status is ScopeStatus.ALLOWED
    assert d.resolved_path.startswith(root)


def test_nested_in_scope_allowed(boundary):
    b, root = boundary
    d = b.check("a/b/c.py")
    assert d.status is ScopeStatus.ALLOWED


# --------------------------------------------------------------------------- #
# Fail-closed escapes
# --------------------------------------------------------------------------- #
def test_traversal_denied(boundary):
    b, root = boundary
    d = b.check("../escape.py")
    assert d.status is ScopeStatus.DENIED


def test_absolute_outside_denied(boundary):
    b, root = boundary
    d = b.check("/etc/passwd")
    assert d.status is ScopeStatus.DENIED


def test_require_raises_on_denial(boundary):
    b, root = boundary
    with pytest.raises(FileSafetyError):
        b.require("../../secret")


def test_missing_root_rejected():
    with pytest.raises(FileSafetyError):
        FileSafetyBoundary("/nonexistent/path/xyz")


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_decision_has_evidence(boundary):
    b, root = boundary
    d = b.check("src/main.py")
    assert d.evidence_id.startswith("ev-")
    assert len(d.content_hash) == 64


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports beyond os (allowed for path safety)
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "filesafety.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    # os is permitted here (path resolution for scope enforcement); only
    # subprocess/providers/filesystem adapters are forbidden.
    forbidden = {"subprocess", "aios.runtime.providers", "aios.runtime.filesystem"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not (imported & forbidden), f"forbidden imports: {imported & forbidden}"
