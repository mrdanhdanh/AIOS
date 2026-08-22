"""Asset Pipeline — registry, capability routing, validation (TASK-081, M11).

Manages asset lifecycle (create, validate, version, route) via an
Asset Capability Registry and policy-driven routing to the capability/tool
that handles a given asset type. Built on ``aios.capability`` + Evidence
(T001 Rule 5). Does NOT replace the capability system.

Layering: ``unknown`` (infra) layer — stdlib + ``aios.governance.evidence``
+ ``aios.capability`` + ``aios.visual_evidence`` only.
"""

from __future__ import annotations

from .pipeline import (
    AssetRecord,
    AssetRegistry,
    AssetCapabilityRegistry,
    AssetRouter,
    AssetValidator,
    AssetError,
)

__all__ = [
    "AssetRecord",
    "AssetRegistry",
    "AssetCapabilityRegistry",
    "AssetRouter",
    "AssetValidator",
    "AssetError",
]
