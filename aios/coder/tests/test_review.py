"""Unit + Contract + Integration + Architecture + Regression tests (TASK-129)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from aios.coder.review import CodeReviewAgent, ReviewError, Severity, Verdict


# --------------------------------------------------------------------------- #
# Review artifact -> findings + verdict
# --------------------------------------------------------------------------- #
def test_review_clean_approves():
    agent = CodeReviewAgent()
    report = agent.review("def f():\n    return 1\n", artifact_ref="art-1")
    assert report.verdict is Verdict.APPROVE
    assert report.findings == []


def test_review_blocking_finding_blocks():
    agent = CodeReviewAgent()
    report = agent.review("import subprocess\n", artifact_ref="art-1")
    assert report.verdict is Verdict.BLOCK
    assert any(f.severity is Severity.BLOCK for f in report.findings)


def test_review_warn_requests_changes():
    agent = CodeReviewAgent()
    report = agent.review("x = eval('1+1')\n", artifact_ref="art-1")
    assert report.verdict is Verdict.REQUEST_CHANGES


# --------------------------------------------------------------------------- #
# Fail-closed / policy
# --------------------------------------------------------------------------- #
def test_policy_rejected():
    agent = CodeReviewAgent()
    with pytest.raises(ReviewError):
        agent.review("def f():\n    pass\n", policy_ok=False)


def test_agent_id_required():
    with pytest.raises(ReviewError):
        CodeReviewAgent(agent_id="")


# --------------------------------------------------------------------------- #
# Deterministic
# --------------------------------------------------------------------------- #
def test_deterministic_same_content_same_verdict():
    a = CodeReviewAgent().review("import subprocess\n")
    b = CodeReviewAgent().review("import subprocess\n")
    assert a.verdict == b.verdict
    assert a.content_hash == b.content_hash


# --------------------------------------------------------------------------- #
# Provenance
# --------------------------------------------------------------------------- #
def test_finding_has_evidence():
    agent = CodeReviewAgent()
    report = agent.review("import subprocess\n")
    assert report.evidence_id.startswith("ev-")
    for f in report.findings:
        assert f.evidence_id.startswith("ev-")


# --------------------------------------------------------------------------- #
# Architecture — no forbidden imports
# --------------------------------------------------------------------------- #
def test_module_has_no_forbidden_imports():
    src = Path(__file__).resolve().parents[1] / "review.py"
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
