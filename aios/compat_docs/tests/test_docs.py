"""Tests for TASK-088 — Docs & ADR — Compatibility (Test Matrix)."""

from __future__ import annotations

import pytest

from aios.compat_docs.docs import (
    CompatDoc,
    CompatDocReviewer,
    DocStatus,
    REQUIRED_COVERED_TASKS,
)


def _good_doc() -> CompatDoc:
    return CompatDoc(
        doc_id="compat-docs",
        covers=list(REQUIRED_COVERED_TASKS),
        adr_ref="ADR-Compatibility",
        rationale="AIOS adopts semver with a 180d deprecation window so 1.x "
                  "consumers are never broken silently.",
        status=DocStatus.PUBLISHED,
        evidence_ref="ev-docs-1",
        references=["T084", "T085", "T086", "T087", "ADR-Compatibility"],
    )


def test_docs_cover_t084_t087_pass():
    reviewer = CompatDocReviewer()
    res = reviewer.review(_good_doc())
    assert res.approved is True
    assert res.missing_coverage == []


def test_adr_missing_rationale_blocked():
    reviewer = CompatDocReviewer()
    doc = _good_doc()
    doc.rationale = ""  # ADR present but no rationale
    res = reviewer.review(doc)
    assert res.approved is False
    assert res.missing_rationale is True


def test_doc_stale_vs_impl_blocked():
    reviewer = CompatDocReviewer()
    doc = _good_doc()
    doc.evidence_ref = ""  # PUBLISHED but no provenance link -> stale
    res = reviewer.review(doc)
    assert res.approved is False
    assert res.stale is True


def test_doc_link_task_provenance():
    reviewer = CompatDocReviewer()
    doc = _good_doc()
    assert reviewer.validate_references(doc) is True
    assert reviewer.provenance_complete(doc) is True


def test_same_content_same_review_deterministic():
    reviewer = CompatDocReviewer()
    h1 = reviewer.review_hash(_good_doc())
    h2 = reviewer.review_hash(_good_doc())
    assert h1 == h2
    r1 = reviewer.review(_good_doc())
    r2 = reviewer.review(_good_doc())
    assert r1.approved == r2.approved


def test_doc_reference_valid_no_404():
    reviewer = CompatDocReviewer()
    doc = _good_doc()
    doc.references.append("T999")  # unknown reference -> 404
    res = reviewer.review(doc)
    assert res.approved is False
    assert "T999" in res.broken_references
    assert reviewer.validate_references(doc) is False


def test_missing_coverage_blocked():
    reviewer = CompatDocReviewer()
    doc = _good_doc()
    doc.covers = ["T084", "T085", "T086"]  # missing T087
    res = reviewer.review(doc)
    assert res.approved is False
    assert "T087" in res.missing_coverage
