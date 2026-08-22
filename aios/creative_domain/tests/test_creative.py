"""Tests for Creative Domain + Vendor Integrity (TASK-082, M11)."""

from __future__ import annotations

import pytest

from aios.creative_domain.creative import (
    CreativeAsset,
    VendorIntegrity,
    ReferenceAsset,
    CreativeCapabilityRegistry,
    CreativeError,
    sha256,
)


def _asset(vendor_prov="sig-vendor-1", lic="mit", ctype="image"):
    return CreativeAsset(
        asset_id="c1", creative_type=ctype, vendor_id="v1",
        vendor_provenance=vendor_prov, license=lic,
        content_hash=sha256("pixels"), evidence_ref="ev-1",
    )


def test_vendor_integrity_accepts_with_provenance():
    vi = VendorIntegrity()
    assert vi.verify(_asset()) is True


def test_vendor_integrity_rejects_missing_provenance():
    vi = VendorIntegrity()
    assert vi.verify(_asset(vendor_prov="")) is False
    with pytest.raises(CreativeError):
        vi.require_provenance(_asset(vendor_prov=""))


def test_vendor_integrity_rejects_bad_license():
    vi = VendorIntegrity()
    assert vi.verify(_asset(lic="gpl-violation")) is False


def test_reference_requires_evidence():
    ref = ReferenceAsset()
    with pytest.raises(CreativeError):
        ref.approve("r1", sha256("gold"), evidence_ref="")


def test_reference_compare_deterministic():
    ref = ReferenceAsset()
    ref.approve("r1", sha256("gold"), evidence_ref="ev-1")
    a_same = _asset()
    a_same.content_hash = sha256("gold")
    a_diff = _asset()
    a_diff.content_hash = sha256("other-content-here")
    assert ref.compare("r1", a_same) == 0.0
    assert ref.compare("r1", a_diff) > 0.0


def test_reference_compare_unapproved_raises():
    ref = ReferenceAsset()
    with pytest.raises(CreativeError):
        ref.compare("missing", _asset())


def test_creative_capability_registry():
    reg = CreativeCapabilityRegistry()
    reg.register("image", "cap.img")
    assert "cap.img" in reg.capable("image")
    with pytest.raises(CreativeError):
        reg.register("text", "cap.txt")


def test_deterministic_verify_same_asset():
    vi = VendorIntegrity()
    a = _asset()
    b = _asset()
    assert vi.verify(a) == vi.verify(b)
