"""Tests for Verification Integrity gate (TASK-078, M11)."""

from __future__ import annotations

import pytest

from aios.verification_integrity.integrity import (
    IntegrityChecker,
    IntegrityError,
    VerdictClass,
    sha256,
)


def _evidence(ev_id="ev-1", content="result: pass", verdict="pass", prov=None):
    return {
        "id": ev_id,
        "content": content,
        "hash": sha256(content),
        "verifier_version": "1.0.0",
        "verifier_config": "strict",
        "verdict": verdict,
        "provenance": prov if prov is not None else [type("L", (), {"evidence_id": ev_id})()],
    }


def test_evidence_hash_match_passes():
    chk = IntegrityChecker()
    ev = _evidence()
    rep = chk.evaluate(
        ev["id"], ev["content"], ev["hash"],
        ev["verifier_version"], ev["verifier_config"], ev["verdict"], ev["provenance"],
    )
    assert rep.tampered is False
    assert rep.promoted_to_pass is True
    assert rep.provenance_complete is True


def test_tampered_evidence_rejected():
    chk = IntegrityChecker()
    ev = _evidence()
    rep = chk.evaluate(
        ev["id"], "altered content", ev["hash"],
        ev["verifier_version"], ev["verifier_config"], "pass", ev["provenance"],
    )
    assert rep.tampered is True
    assert rep.promoted_to_pass is False
    assert any("tamper" in n for n in rep.notes)


def test_unknown_verdict_not_promoted():
    chk = IntegrityChecker()
    ev = _evidence(verdict="unknown")
    rep = chk.evaluate(
        ev["id"], ev["content"], ev["hash"],
        ev["verifier_version"], ev["verifier_config"], ev["verdict"], ev["provenance"],
    )
    assert rep.verdict_class == "unknown"
    assert rep.promoted_to_pass is False


def test_inconclusive_verdict_not_promoted():
    chk = IntegrityChecker()
    ev = _evidence(verdict="inconclusive")
    rep = chk.evaluate(
        ev["id"], ev["content"], ev["hash"],
        ev["verifier_version"], ev["verifier_config"], ev["verdict"], ev["provenance"],
    )
    assert rep.verdict_class == "inconclusive"
    assert rep.promoted_to_pass is False


def test_verifier_lock_detects_change():
    chk = IntegrityChecker()
    chk.lock_verifier("run-1", "1.0.0", "strict")
    assert chk.verifier_changed("run-1", "1.0.0", "strict") is False
    assert chk.verifier_changed("run-1", "2.0.0", "strict") is True
    assert chk.verifier_changed("run-1", "1.0.0", "loose") is True


def test_promotes_to_pass_only_explicit():
    assert IntegrityChecker.promotes_to_pass("pass") is True
    assert IntegrityChecker.promotes_to_pass("fail") is False
    assert IntegrityChecker.promotes_to_pass("unknown") is False
    assert IntegrityChecker.promotes_to_pass("inconclusive") is False
    assert IntegrityChecker.promotes_to_pass(None) is False


def test_provenance_incomplete():
    chk = IntegrityChecker()
    ev = _evidence(prov=[])
    rep = chk.evaluate(
        ev["id"], ev["content"], ev["hash"],
        ev["verifier_version"], ev["verifier_config"], "pass", ev["provenance"],
    )
    assert rep.provenance_complete is False


def test_deterministic_same_input_same_verdict():
    chk = IntegrityChecker()
    a = chk.evaluate("e", "x", sha256("x"), "1.0", "c", "pass", [type("L", (), {"evidence_id": "e"})()])
    b = chk.evaluate("e", "x", sha256("x"), "1.0", "c", "pass", [type("L", (), {"evidence_id": "e"})()])
    assert a.to_dict() == b.to_dict()
