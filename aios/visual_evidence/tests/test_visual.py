"""Tests for Visual Evidence + Visual Regression (TASK-080, M11)."""

from __future__ import annotations

import pytest

from aios.visual_evidence.visual import (
    VisualCapture,
    UIStateContract,
    VisualRegression,
    VisualError,
)


def test_capture_produces_deterministic_hash():
    cap = VisualCapture()
    h1, _ = cap.capture("<html>ok</html>", "cfg")
    h2, _ = cap.capture("<html>ok</html>", "cfg")
    assert h1 == h2


def test_capture_differs_on_state_change():
    cap = VisualCapture()
    h1, _ = cap.capture("<html>ok</html>")
    h2, _ = cap.capture("<html>changed</html>")
    assert h1 != h2


def test_baseline_requires_evidence():
    contract = UIStateContract(valid_states=["login", "home"])
    with pytest.raises(VisualError):
        contract.approve_baseline("login", "abc", evidence_ref="")


def test_baseline_approve_and_regression_flag():
    cap = VisualCapture()
    base_hash, _ = cap.capture("<html>baseline</html>")
    contract = UIStateContract(valid_states=["page"])
    contract.approve_baseline("page", base_hash, evidence_ref="ev-1")

    reg = VisualRegression(threshold=0.05)
    # Same state -> no regression.
    same_hash, _ = cap.capture("<html>baseline</html>")
    ve = reg.evaluate(same_hash, contract.baseline_hash("page"), "page", "ev-2")
    assert ve.regression is False
    assert ve.diff_score == 0.0

    # Different state -> regression flagged.
    diff_hash, _ = cap.capture("<html>totally different content here</html>")
    ve2 = reg.evaluate(diff_hash, contract.baseline_hash("page"), "page", "ev-3")
    assert ve2.regression is True


def test_baseline_change_requires_evidence():
    cap = VisualCapture()
    base_hash, _ = cap.capture("<html>v1</html>")
    contract = UIStateContract(valid_states=["page"])
    contract.approve_baseline("page", base_hash, evidence_ref="ev-1")
    with pytest.raises(VisualError):
        contract.change_baseline("page", "newhash", evidence_ref="")
    contract.change_baseline("page", "newhash", evidence_ref="ev-2")
    assert contract.baseline_hash("page") == "newhash"


def test_regression_without_baseline_raises():
    reg = VisualRegression()
    with pytest.raises(VisualError):
        reg.evaluate("hash", "", "page", "ev-1")
