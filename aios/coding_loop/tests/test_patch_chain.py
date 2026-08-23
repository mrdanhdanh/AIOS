"""Tests for context refresh + patch chain (T152)."""

import pytest

from aios.coding_loop import (
    ContextRefreshPatchChain,
    ProgressRegressionDetector,
    VerifyStatus,
    VerificationGate,
)
from aios.coding_loop._common import CodingLoopError


def _verified():
    d = ProgressRegressionDetector(baseline=0.5)
    prog = d.detect("loop1", "plan1", 0.8, evidence_ref="ev1")
    return VerificationGate().verify(prog, output_hash="abc", evidence_ref="ev1")


def test_refresh_context_deterministic():
    c = ContextRefreshPatchChain()
    assert c.refresh_context("REFRESHING") == c.refresh_context("REFRESHING")
    assert c.refresh_context("REFRESHING") != c.refresh_context("SAFETY")


def test_chain_with_verified_output():
    c = ContextRefreshPatchChain()
    vr = _verified()
    chain = c.refresh_and_chain(vr, "ctx-0", "snap-0", "snap-0", patch_links=["p1"])
    assert chain.chain_id
    assert chain.snapshot_ref == "snap-0"
    assert len(chain.patch_links) == 1


def test_snapshot_mismatch_rejected():
    c = ContextRefreshPatchChain()
    vr = _verified()
    with pytest.raises(CodingLoopError):
        c.refresh_and_chain(vr, "ctx-0", "snap-0", "snap-1")  # fail-closed (T137)


def test_unverified_output_rejected():
    c = ContextRefreshPatchChain()
    d = ProgressRegressionDetector(baseline=0.5)
    prog = d.detect("loop1", "plan1", 0.2, evidence_ref="ev1")  # regression -> FAIL
    vr = VerificationGate().verify(prog, "abc", evidence_ref="ev1")
    assert vr.verification_result == VerifyStatus.FAIL
    with pytest.raises(CodingLoopError):
        c.refresh_and_chain(vr, "ctx-0", "snap-0", "snap-0")  # fail-closed (T078)


def test_duplicate_chain_id_rejected():
    c = ContextRefreshPatchChain()
    vr = _verified()
    c.refresh_and_chain(vr, "ctx-0", "snap-0", "snap-0", chain_id="chain1")
    with pytest.raises(CodingLoopError):
        c.refresh_and_chain(vr, "ctx-0", "snap-0", "snap-0", chain_id="chain1")


def test_chain_requires_provenance():
    c = ContextRefreshPatchChain()
    from aios.coding_loop.verification_gate import VerificationResult

    bad = VerificationResult("v1", "p1", VerifyStatus.PASS, True, evidence_ref="ev-tmp")
    object.__setattr__(bad, "evidence_ref", "")
    with pytest.raises(CodingLoopError):
        c.refresh_and_chain(bad, "ctx-0", "snap-0", "snap-0")


def test_provenance_hash():
    c = ContextRefreshPatchChain()
    vr = _verified()
    chain = c.refresh_and_chain(vr, "ctx-0", "snap-0", "snap-0")
    prov = c.provenance(chain.chain_id)
    assert prov["content_hash"]
    assert prov["snapshot_ref"] == "snap-0"
