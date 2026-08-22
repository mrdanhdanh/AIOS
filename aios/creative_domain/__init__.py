"""Creative Domain — creative assets, vendor integrity, reference (TASK-082, M11).

Extends AIOS into the creative domain (image/audio/video/design) on top of the
Asset Pipeline (T081) + Evidence (T001). Adds Vendor Integrity (provenance of
the generating vendor/model) and Reference Assets (golden baselines).

Layering: ``unknown`` (infra) layer — stdlib + ``aios.governance.evidence``
+ ``aios.asset_pipeline`` + ``aios.visual_evidence`` only.
"""

from __future__ import annotations

from .creative import (
    CreativeAsset,
    VendorIntegrity,
    ReferenceAsset,
    CreativeCapabilityRegistry,
    CreativeError,
)

__all__ = [
    "CreativeAsset",
    "VendorIntegrity",
    "ReferenceAsset",
    "CreativeCapabilityRegistry",
    "CreativeError",
]
