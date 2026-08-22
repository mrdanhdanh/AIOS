"""Creative Domain — vendor integrity + reference assets (TASK-082, M11).

* ``CreativeAsset`` — schema for creative asset types (image/audio/video/design)
  with vendor provenance + license.
* ``VendorIntegrity`` — verifies the generating vendor/model provenance
  (fail-closed: missing provenance -> reject).
* ``ReferenceAsset`` — golden baseline approved via evidence before use.
* ``CreativeCapabilityRegistry`` — registers creative types via the Asset
  Capability Registry (T081).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


class CreativeError(Exception):
    """Raised on creative-domain contract violations (fail-closed)."""


def sha256(content: bytes | str) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


CREATIVE_TYPES = ("image", "audio", "video", "design")

# Licenses considered acceptable for ingestion.
ALLOWED_LICENSES = ("mit", "apache-2.0", "cc-by", "cc0", "proprietary-approved", "internal")


@dataclass
class CreativeAsset:
    """A creative asset with vendor provenance + license."""

    asset_id: str
    creative_type: str
    vendor_id: str
    vendor_provenance: str  # signed provenance token / hash
    reference_asset_id: str = ""
    license: str = ""
    content_hash: str = ""
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "creative_type": self.creative_type,
            "vendor_id": self.vendor_id,
            "vendor_provenance": self.vendor_provenance,
            "reference_asset_id": self.reference_asset_id,
            "license": self.license,
            "content_hash": self.content_hash,
            "evidence_ref": self.evidence_ref,
        }


class VendorIntegrity:
    """Verifies vendor/model provenance of a creative asset (fail-closed)."""

    def verify(self, asset: CreativeAsset) -> bool:
        """Reject if provenance missing, type invalid, or license disallowed."""
        if not asset.vendor_provenance:
            return False
        if asset.creative_type not in CREATIVE_TYPES:
            return False
        if asset.license and asset.license.lower() not in ALLOWED_LICENSES:
            return False
        return True

    def require_provenance(self, asset: CreativeAsset) -> None:
        if not self.verify(asset):
            raise CreativeError(
                "creative asset missing vendor provenance / invalid -> rejected (fail-closed)"
            )


class ReferenceAsset:
    """Golden baseline asset, approved via evidence before comparison."""

    def __init__(self) -> None:
        self._refs: dict[str, dict[str, str]] = {}
        self._approved: set[str] = set()

    def approve(self, reference_id: str, content_hash: str, evidence_ref: str = "") -> None:
        if not evidence_ref:
            raise CreativeError("reference asset approval requires evidence_ref")
        self._refs[reference_id] = {"content_hash": content_hash, "evidence_ref": evidence_ref}
        self._approved.add(reference_id)

    def is_approved(self, reference_id: str) -> bool:
        return reference_id in self._approved

    def compare(self, reference_id: str, asset: CreativeAsset) -> float:
        """Return diff score vs the approved reference (0.0 == identical)."""
        if not self.is_approved(reference_id):
            raise CreativeError(f"reference {reference_id} not approved before comparison")
        ref_hash = self._refs[reference_id]["content_hash"]
        if not asset.content_hash:
            raise CreativeError("asset has no content_hash")
        if ref_hash == asset.content_hash:
            return 0.0
        diff = sum(1 for a, b in zip(ref_hash, asset.content_hash) if a != b)
        return diff / max(len(ref_hash), 1)


class CreativeCapabilityRegistry:
    """Registers creative types via the Asset Capability Registry (T081)."""

    def __init__(self, asset_cap_registry: Any | None = None) -> None:
        # Accept the AssetCapabilityRegistry duck-typed (register_capability).
        self._asset_caps = asset_cap_registry
        self._creative_caps: dict[str, set[str]] = {}

    def register(self, creative_type: str, capability_id: str) -> None:
        if creative_type not in CREATIVE_TYPES:
            raise CreativeError(f"{creative_type} is not a creative type")
        self._creative_caps.setdefault(creative_type, set()).add(capability_id)
        if self._asset_caps is not None:
            self._asset_caps.register_capability(creative_type, capability_id)

    def capable(self, creative_type: str) -> list[str]:
        return sorted(self._creative_caps.get(creative_type, set()))
