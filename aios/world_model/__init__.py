"""World Model (TASK-052).

Models the *current* state of the world/system AIOS acts upon, strictly
separated from Memory. State is updated only through observations/evidence
with provenance. No LLM is used as source of truth.
"""

from aios.world_model.contracts import (
    WorldEntity,
    WorldObservation,
    WorldRelation,
    WorldSnapshot,
    WorldState,
    WorldTransition,
)
from aios.world_model.engine import WorldModel

__all__ = [
    "WorldEntity",
    "WorldObservation",
    "WorldRelation",
    "WorldSnapshot",
    "WorldState",
    "WorldTransition",
    "WorldModel",
]
