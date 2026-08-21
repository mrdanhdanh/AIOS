"""Tests for verification pipeline."""

from __future__ import annotations

from aios.harness.verification import EvidencePackage, VerificationPipeline, Verdict


class TestVerificationPipeline:
    def test_all_pass(self) -> None:
        pipe = VerificationPipeline()
        pipe.add_precondition(lambda: True)
        pipe.add_postcondition(lambda: True)
        result = pipe.verify("run-1")
        assert result.verdict == Verdict.PASS
        assert result.evidence is not None

    def test_precondition_fail(self) -> None:
        pipe = VerificationPipeline()
        pipe.add_precondition(lambda: False)
        result = pipe.verify("run-1")
        assert result.verdict == Verdict.FAIL

    def test_postcondition_fail(self) -> None:
        """AC-030-01: Execution succeeds but post-condition fails → FAIL."""
        pipe = VerificationPipeline()
        pipe.add_precondition(lambda: True)
        pipe.add_postcondition(lambda: False)
        result = pipe.verify("run-1")
        assert result.verdict == Verdict.FAIL

    def test_invariant_fail(self) -> None:
        pipe = VerificationPipeline()
        pipe.add_precondition(lambda: True)
        pipe.add_postcondition(lambda: True)
        pipe.add_invariant(lambda: False)
        result = pipe.verify("run-1")
        assert result.verdict == Verdict.FAIL

    def test_no_checks_inconclusive(self) -> None:
        """AC-030-09: Missing evidence → INCONCLUSIVE."""
        pipe = VerificationPipeline()
        result = pipe.verify("run-1")
        assert result.verdict == Verdict.INCONCLUSIVE

    def test_evidence_created(self) -> None:
        """AC-030-05: Every run creates Evidence Package."""
        pipe = VerificationPipeline()
        pipe.add_precondition(lambda: True)
        result = pipe.verify("run-1")
        assert result.evidence is not None
        assert result.evidence.run_id == "run-1"
