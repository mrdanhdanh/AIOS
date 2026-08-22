"""Tests for TASK-093 — Behavioral Spec + ADR-0008 (Test Matrix)."""

from __future__ import annotations

from pathlib import Path

from aios.behavioral_docs.docs import (
    BehavioralDoc,
    BehavioralDocReviewer,
    DocStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[3]  # aios/behavioral_docs/tests -> root


def _good_doc() -> BehavioralDoc:
    return BehavioralDoc(
        doc_id="behavioral-spec",
        covers=["TASK-089", "TASK-090", "TASK-091", "TASK-092", "TASK-093"],
        adr_ref="ADR-0008",
        status=DocStatus.PUBLISHED,
        references=[
            "aios/behavioral/behavioral.py",
            "aios/harness_coverage/coverage.py",
            "aios/meta_harness/meta.py",
            "aios/readiness_trust/trust.py",
            "docs/adr/ADR-0008.md",
            "docs/detailtask/T089.md",
        ],
        rationale="Behavioral conformance guarantees observable behavior matches spec.",
        evidence_ref="ev-doc-1",
    )


def test_docs_cover_m13_pass():
    reviewer = BehavioralDocReviewer(repo_root=REPO_ROOT)
    result = reviewer.review(_good_doc())
    assert result.covers_m13 is True
    assert result.passed is True


def test_adr_missing_rationale_blocked():
    reviewer = BehavioralDocReviewer(repo_root=REPO_ROOT)
    doc = _good_doc()
    doc.rationale = ""
    doc.adr_ref = "ADR-XXXX"
    result = reviewer.review(doc)
    assert result.adr_has_rationale is False
    assert result.passed is False


def test_stale_reference_blocked():
    reviewer = BehavioralDocReviewer(repo_root=REPO_ROOT)
    doc = _good_doc()
    doc.references.append("aios/does_not_exist/module.py")
    result = reviewer.review(doc)
    assert result.no_stale is False
    assert result.links_valid is False
    assert result.passed is False


def test_doc_link_provenance():
    reviewer = BehavioralDocReviewer(repo_root=REPO_ROOT)
    assert reviewer.provenance_complete(_good_doc()) is True


def test_same_content_same_review_deterministic():
    reviewer = BehavioralDocReviewer(repo_root=REPO_ROOT)
    r1 = reviewer.review(_good_doc())
    r2 = reviewer.review(_good_doc())
    assert reviewer.review_hash(r1) == reviewer.review_hash(r2)
    assert r1.passed == r2.passed


def test_missing_m13_coverage_blocked():
    reviewer = BehavioralDocReviewer(repo_root=REPO_ROOT)
    doc = _good_doc()
    doc.covers = ["TASK-089", "TASK-090"]  # missing T091-T093
    result = reviewer.review(doc)
    assert result.covers_m13 is False
    assert result.passed is False
