"""Asset Pipeline — registry, capability registry, routing, validation (T081).

* ``AssetRecord`` — versioned asset with content_hash (T001 Rule 5).
* ``AssetRegistry`` — stores versioned assets; lookup by id/type.
* ``AssetCapabilityRegistry`` — maps asset_type -> capable capability ids.
* ``AssetRouter`` — policy-driven selection of a capable capability (fail-closed:
  unvalidated or unregistered asset types are never routed).
* ``AssetValidator`` — integrity (hash) + schema validation before routing.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


class AssetError(Exception):
    """Raised on asset pipeline contract violations (fail-closed)."""


def sha256(content: bytes | str) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


@dataclass
class AssetRecord:
    """A versioned asset with integrity hash and provenance."""

    asset_id: str
    asset_type: str
    version: str
    content_hash: str
    capable_capabilities: list[str] = field(default_factory=list)
    evidence_ref: str = ""
    schema: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "version": self.version,
            "content_hash": self.content_hash,
            "capable_capabilities": list(self.capable_capabilities),
            "evidence_ref": self.evidence_ref,
        }


class AssetRegistry:
    """Stores versioned assets keyed by (asset_id, version)."""

    def __init__(self) -> None:
        self._assets: dict[tuple[str, str], AssetRecord] = {}

    def register(self, asset: AssetRecord) -> None:
        self._assets[(asset.asset_id, asset.version)] = asset

    def get(self, asset_id: str, version: str) -> Optional[AssetRecord]:
        return self._assets.get((asset_id, version))

    def latest(self, asset_id: str) -> Optional[AssetRecord]:
        versions = [a for (aid, _), a in self._assets.items() if aid == asset_id]
        if not versions:
            return None
        return sorted(versions, key=lambda a: a.version)[-1]


class AssetCapabilityRegistry:
    """Maps asset_type -> set of capable capability ids."""

    def __init__(self) -> None:
        self._map: dict[str, set[str]] = {}

    def register_capability(self, asset_type: str, capability_id: str) -> None:
        self._map.setdefault(asset_type, set()).add(capability_id)

    def capable_capabilities(self, asset_type: str) -> list[str]:
        return sorted(self._map.get(asset_type, set()))

    def has_capability(self, asset_type: str) -> bool:
        return bool(self._map.get(asset_type))


class AssetValidator:
    """Validates asset integrity (hash) + schema before routing."""

    # Minimal schema: asset_type must match a known pattern; required keys present.
    _TYPE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

    def validate(self, asset: AssetRecord, content: bytes | str) -> bool:
        """Fail-closed: hash mismatch or bad schema -> invalid."""
        if not self._TYPE_RE.match(asset.asset_type):
            return False
        if sha256(content) != asset.content_hash:
            return False
        for key in asset.schema.get("required_fields", []):
            if key not in asset.schema.get("fields", {}):
                return False
        return True


class AssetRouter:
    """Routes a validated asset to a capable capability (policy-driven)."""

    def __init__(
        self,
        capability_registry: AssetCapabilityRegistry,
        validator: Optional[AssetValidator] = None,
    ) -> None:
        self._caps = capability_registry
        self._validator = validator or AssetValidator()

    def route(self, asset: AssetRecord, content: bytes | str,
              policy: str = "first") -> str:
        """Return the selected capability id (fail-closed).

        Raises AssetError if the asset is invalid or has no capable capability.
        """
        if not self._validator.validate(asset, content):
            raise AssetError("asset failed validation -> not routed (fail-closed)")
        capable = self._caps.capable_capabilities(asset.asset_type)
        if not capable:
            raise AssetError(
                f"no capable capability for asset_type {asset.asset_type} -> not routed"
            )
        if policy == "first":
            return capable[0]
        if policy == "last":
            return capable[-1]
        if policy in capable:
            return policy
        raise AssetError(f"policy capability {policy} not capable for asset_type")
