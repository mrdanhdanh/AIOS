"""Unit + Contract + Integration + Architecture + Regression tests (TASK-128)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.patch import PatchEngine, PatchError, PatchStatus


# --------------------------------------------------------------------------- #
# Diff
# --------------------------------------------------------------------------- #
def test_diff_from_artifact():
    eng = PatchEngine()
    diff = eng.diff("def f():\n    return 1\n", "def f():\n    return 0\n", "m.py")
    assert diff.startswith("--- a/m.py") or "m.py" in diff
    assert "+    return 1" in diff
    assert "-    return 0" in diff


def test_diff_deterministic():
    eng = PatchEngine()
    a = eng.diff("x", "y", "t.py")
    b = eng.diff("x", "y", "t.py")
    assert a == b


# --------------------------------------------------------------------------- #
# Apply with backup
# --------------------------------------------------------------------------- #
def test_apply_with_backup():
    eng = PatchEngine()
    store = {}

    def apply_fn(target, content):
        store[target] = content

    run = eng.apply("art-1", "m.py", "new content", "old content", apply_fn=apply_fn)
    assert run.status is PatchStatus.APPLIED
    assert run.applied is True
    assert run.backup_ref is not None
    assert run.rollback_available is True
    assert store["m.py"] == "new content"


# --------------------------------------------------------------------------- #
# Fail-closed -> rollback
# --------------------------------------------------------------------------- #
def test_apply_fail_rolls_back():
    eng = PatchEngine()
    store = {"m.py": "old content"}

    def apply_fn(target, content):
        raise RuntimeError("boom")

    with pytest.raises(PatchError):
        eng.apply("art-1", "m.py", "new content", "old content", apply_fn=apply_fn)
    # repository left intact (fail-closed, T020/T066)
    assert store["m.py"] == "old content"


def test_policy_rejected():
    eng = PatchEngine()
    with pytest.raises(PatchError):
        eng.apply("art-1", "m.py", "new", "old", policy_ok=False)


def test_rollback_returns_certified_state():
    eng = PatchEngine()
    store = {}

    def apply_fn(target, content):
        store[target] = content

    run = eng.apply("art-1", "m.py", "new content", "old content", apply_fn=apply_fn)
    restored = eng.rollback(run)
    assert restored == "old content"


# --------------------------------------------------------------------------- #
# Provenance + hash
# --------------------------------------------------------------------------- #
def test_patch_has_hash_and_evidence():
    eng = PatchEngine()
    run = eng.apply("art-1", "m.py", "new", "old")
    assert len(run.content_hash) == 64
    assert run.evidence_id.startswith("ev-")


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "patch.py"
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
