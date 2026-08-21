"""Upgrade manifest schema — describes an upgrade operation.

Each upgrade has a manifest with source/target versions,
contract changes, migration steps, and validation checks.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class UpgradeStepType(str, Enum):
    """Types of migration steps."""
    SCHEMA = "schema"
    CONTRACT = "contract"
    DATA = "data"
    CONFIG = "config"
    DEPENDENCY = "dependency"


@dataclass
class UpgradeStep:
    """A single migration step within an upgrade."""

    step_id: str
    step_type: UpgradeStepType
    description: str = ""
    reversible: bool = True
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_type": self.step_type.value,
            "description": self.description,
            "reversible": self.reversible,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
        }


@dataclass
class UpgradeManifest:
    """Complete upgrade manifest with all metadata.

    AC-020-01: Upgrade has preflight via manifest validation.
    """

    upgrade_id: str
    source_version: str
    target_version: str
    steps: list[UpgradeStep] = field(default_factory=list)
    validation_checks: list[str] = field(default_factory=list)
    rollback_supported: bool = True
    created_at: float = field(default_factory=time.time)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def all_reversible(self) -> bool:
        return all(s.reversible for s in self.steps)

    def compute_hash(self) -> str:
        """Compute deterministic hash of the manifest."""
        content = f"{self.upgrade_id}:{self.source_version}:{self.target_version}"
        for step in self.steps:
            content += f":{step.step_id}:{step.step_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "upgrade_id": self.upgrade_id,
            "source_version": self.source_version,
            "target_version": self.target_version,
            "steps": [s.to_dict() for s in self.steps],
            "validation_checks": self.validation_checks,
            "rollback_supported": self.rollback_supported,
            "created_at": self.created_at,
            "content_hash": self.compute_hash(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UpgradeManifest:
        """Parse manifest from dictionary."""
        steps = [
            UpgradeStep(
                step_id=s["step_id"],
                step_type=UpgradeStepType(s["step_type"]),
                description=s.get("description", ""),
                reversible=s.get("reversible", True),
                preconditions=s.get("preconditions", []),
                postconditions=s.get("postconditions", []),
            )
            for s in data.get("steps", [])
        ]
        return cls(
            upgrade_id=data["upgrade_id"],
            source_version=data["source_version"],
            target_version=data["target_version"],
            steps=steps,
            validation_checks=data.get("validation_checks", []),
            rollback_supported=data.get("rollback_supported", True),
            created_at=data.get("created_at", time.time()),
        )
