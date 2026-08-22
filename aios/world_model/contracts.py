"""World Model contracts (TASK-052)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ObservationType(str, Enum):
    HEARTBEAT = "heartbeat"
    METRIC = "metric"
    EVENT = "event"
    STATE_CHANGE = "state_change"
    EXTERNAL = "external"


@dataclass
class WorldEntity:
    entity_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    type: str = ""
    version: int = 1
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    provenance: list[str] = field(default_factory=list)
    confidence: float = 1.0
    status: EntityStatus = EntityStatus.UNKNOWN
    scope: str = "default"
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "type": self.type,
            "version": self.version,
            "timestamp": self.timestamp,
            "source": self.source,
            "provenance": list(self.provenance),
            "confidence": self.confidence,
            "status": self.status.value,
            "scope": self.scope,
            "attributes": dict(self.attributes),
            "relations": list(self.relations),
        }


@dataclass
class WorldRelation:
    relation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    source_entity: str = ""
    target_entity: str = ""
    relation_type: str = ""
    timestamp: float = field(default_factory=time.time)
    provenance: list[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_entity": self.source_entity,
            "target_entity": self.target_entity,
            "relation_type": self.relation_type,
            "provenance": list(self.provenance),
            "confidence": self.confidence,
        }


@dataclass
class WorldObservation:
    observation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    type: ObservationType = ObservationType.EVENT
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    provenance: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    scope: str = "default"

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "provenance": list(self.provenance),
            "payload": dict(self.payload),
            "confidence": self.confidence,
            "scope": self.scope,
        }


@dataclass
class WorldTransition:
    transition_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    entity_id: str = ""
    from_status: str = ""
    to_status: str = ""
    observation_ref: str = ""
    timestamp: float = field(default_factory=time.time)
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "entity_id": self.entity_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "observation_ref": self.observation_ref,
            "provenance": list(self.provenance),
        }


@dataclass
class WorldSnapshot:
    snapshot_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: float = field(default_factory=time.time)
    version: int = 1
    entities: list[WorldEntity] = field(default_factory=list)
    relations: list[WorldRelation] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "version": self.version,
            "entities": [e.to_dict() for e in self.entities],
            "relations": [r.to_dict() for r in self.relations],
        }


@dataclass
class WorldState:
    """Canonical current modeled state (not memory)."""
    version: int = 1
    timestamp: float = field(default_factory=time.time)
    entities: dict[str, WorldEntity] = field(default_factory=dict)
    relations: dict[str, WorldRelation] = field(default_factory=dict)
    provenance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relations": {k: v.to_dict() for k, v in self.relations.items()},
        }
