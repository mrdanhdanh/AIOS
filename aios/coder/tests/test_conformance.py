"""Unit + Contract + Integration + Architecture + Regression tests (TASK-131)."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

from aios.coder.conformance import (
    CoderConformanceHarness,
    ConformanceStatus,
    SecurityStatus,
)


def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# --------------------------------------------------------------------------- #
# Conformance PASS
# --------------------------------------------------------------------------- #
def test_conformance_pass():
    h = CoderConformanceHarness()
    res = h.check("def f(): pass\n", _h("def f(): pass\n"), "coder-1", True, True)
    assert res.status is ConformanceStatus.PASS
    assert res.security is SecurityStatus.ALLOWED


# --------------------------------------------------------------------------- #
# Fail-closed
# --------------------------------------------------------------------------- #
def test_hash_mismatch_fails():
    h = CoderConformanceHarness()
    res = h.check("x", _h("y"), "coder-1", True, True)
    assert res.status is ConformanceStatus.FAIL


def test_missing_evidence_fails():
    h = CoderConformanceHarness()
    res = h.check("x", _h("x"), "coder-1", False, True)
    assert res.status is ConformanceStatus.FAIL


def test_integrity_not_verified_fails():
    h = CoderConformanceHarness()
    res = h.check("x", _h("x"), "coder-1", True, False)
    assert res.status is ConformanceStatus.FAIL


def test_unauthorized_producer_denied():
    h = CoderConformanceHarness()
    res = h.check("x", _h("x"), "evil", True, True)
    assert res.security is SecurityStatus.DENIED
    assert res.status is ConformanceStatus.FAIL


def test_forbidden_op_denied():
    h = CoderConformanceHarness()
    res = h.check("import subprocess\n", _h("import subprocess\n"), "coder-1", True, True)
    assert res.security is SecurityStatus.DENIED


# --------------------------------------------------------------------------- #
# UNKNOWN never promoted
# --------------------------------------------------------------------------- #
def test_unknown_never_promoted():
    assert CoderConformanceHarness.promote(ConformanceStatus.UNKNOWN) is False
    assert CoderConformanceHarness.promote(ConformanceStatus.PASS) is True
    assert CoderConformanceHarness.promote(ConformanceStatus.FAIL) is False


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_result_has_evidence():
    h = CoderConformanceHarness()
    res = h.check("x", _h("x"), "coder-1", True, True)
    assert res.evidence_id.startswith("ev-")
    assert len(res.content_hash) == 64


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "conformance.py"
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
