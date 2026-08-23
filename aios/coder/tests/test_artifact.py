"""Unit + Contract + Integration + Architecture + Regression tests (TASK-130)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.artifact import (
    ArtifactError,
    ArtifactKind,
    ArtifactStatus,
    CodingArtifactRegistry,
    EvidenceLink,
)


def _link():
    return EvidenceLink(
        evidence_id="ev-1",
        producer="coder-1",
        kind="code",
        content_hash="0" * 64,
        timestamp="2026-08-23T00:00:00Z",
    )


# --------------------------------------------------------------------------- #
# Standardized artifact + hash
# --------------------------------------------------------------------------- #
def test_artifact_standardized_with_hash():
    reg = CodingArtifactRegistry()
    art = reg.create(ArtifactKind.CODE, "def f(): pass\n", "coder-1", [_link()])
    assert art.kind is ArtifactKind.CODE
    assert len(art.content_hash) == 64


# --------------------------------------------------------------------------- #
# Provenance chain
# --------------------------------------------------------------------------- #
def test_artifact_evidence_chain():
    reg = CodingArtifactRegistry()
    art = reg.create(ArtifactKind.PATCH, "diff", "patch-1", [_link()])
    assert len(art.evidence_chain) == 1
    assert art.evidence_chain[0].evidence_id == "ev-1"


# --------------------------------------------------------------------------- #
# Fail-closed integrity gate
# --------------------------------------------------------------------------- #
def test_verify_ok_promotes_verified():
    reg = CodingArtifactRegistry()
    art = reg.create(ArtifactKind.CODE, "x", "coder-1", [_link()])
    verified = reg.verify(art.artifact_id)
    assert verified.status is ArtifactStatus.VERIFIED
    assert verified.integrity_verified is True


def test_verify_missing_evidence_rejects():
    reg = CodingArtifactRegistry()
    art = reg.create(ArtifactKind.CODE, "x", "coder-1")  # no evidence chain
    with pytest.raises(ArtifactError):
        reg.verify(art.artifact_id)


def test_verify_policy_rejected():
    reg = CodingArtifactRegistry()
    art = reg.create(ArtifactKind.CODE, "x", "coder-1", [_link()])
    with pytest.raises(ArtifactError):
        reg.verify(art.artifact_id, policy_ok=False)


# --------------------------------------------------------------------------- #
# Immutable id (T001 Rule 1)
# --------------------------------------------------------------------------- #
def test_artifact_id_immutable_no_reuse():
    reg = CodingArtifactRegistry()
    a = reg.create(ArtifactKind.CODE, "x", "coder-1", [_link()])
    b = reg.create(ArtifactKind.CODE, "y", "coder-1", [_link()])
    assert a.artifact_id != b.artifact_id
    assert a.artifact_id in reg._store


# --------------------------------------------------------------------------- #
# Deterministic
# --------------------------------------------------------------------------- #
def test_verify_deterministic():
    reg = CodingArtifactRegistry()
    a = reg.create(ArtifactKind.CODE, "x", "coder-1", [_link()])
    b = reg.create(ArtifactKind.CODE, "x", "coder-1", [_link()])
    assert reg.verify(a.artifact_id).status == reg.verify(b.artifact_id).status


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "artifact.py"
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
