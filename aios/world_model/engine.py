"""World Model engine (TASK-052).

Observation → Validate → Resolve Entity → Compare Current State →
Generate Transition → Validate Transition → Commit New State.

The World Model is updated only through observations with provenance. It is
strictly separated from Memory and never uses an LLM as source of truth.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aios.world_model.contracts import (
    EntityStatus,
    WorldEntity,
    WorldObservation,
    WorldRelation,
    WorldSnapshot,
    WorldState,
    WorldTransition,
)


class WorldModelError(Exception):
    """Raised when an observation/transition cannot be committed."""


@dataclass
class ObservationResult:
    accepted: bool
    transition: WorldTransition | None = None
    reason: str = ""


class WorldModel:
    """Holds the current modeled world state, updated via observations."""

    def __init__(self) -> None:
        self._state = WorldState()
        self._observations: list[WorldObservation] = []
        self._transitions: list[WorldTransition] = []
        self._snapshots: list[WorldSnapshot] = []
        self._relations: dict[str, WorldRelation] = {}

    # ---- observation ingestion -----------------------------------------
    def observe(self, observation: WorldObservation) -> ObservationResult:
        # Validate: no provenance -> cannot become canonical state.
        if not observation.provenance:
            return ObservationResult(False, None, "observation has no provenance")
        self._observations.append(observation)
        entity = self._resolve_entity(observation)
        if entity is None:
            return ObservationResult(False, None, "could not resolve entity")
        transition = self._generate_transition(entity, observation)
        if transition is None:
            # No state change (idempotent observation) — still accepted.
            return ObservationResult(True, None, "no state change")
        if not self._validate_transition(transition):
            return ObservationResult(False, None, "transition validation failed")
        self._commit_transition(entity, transition)
        self._transitions.append(transition)
        return ObservationResult(True, transition, "committed")

    def _resolve_entity(self, obs: WorldObservation) -> WorldEntity | None:
        eid = obs.payload.get("entity_id") or obs.payload.get("entity")
        if eid and eid in self._state.entities:
            return self._state.entities[eid]
        # Create a new entity from the observation.
        etype = obs.payload.get("entity_type", obs.type.value)
        entity = WorldEntity(
            entity_id=eid or f"ent-{len(self._state.entities)+1}",
            type=str(etype),
            source=obs.source,
            provenance=list(obs.provenance),
            confidence=obs.confidence,
            scope=obs.scope,
            attributes=dict(obs.payload.get("attributes", {})),
        )
        status = obs.payload.get("status")
        if status:
            entity.status = EntityStatus(status) if isinstance(status, str) else EntityStatus.UNKNOWN
        self._state.entities[entity.entity_id] = entity
        return entity

    def _generate_transition(self, entity: WorldEntity, obs: WorldObservation) -> WorldTransition | None:
        new_status = obs.payload.get("status")
        if not new_status or new_status == entity.status.value:
            return None
        return WorldTransition(
            entity_id=entity.entity_id,
            from_status=entity.status.value,
            to_status=str(new_status),
            observation_ref=obs.observation_id,
            provenance=list(obs.provenance),
        )

    def _validate_transition(self, transition: WorldTransition) -> bool:
        # Deterministic: from_status must match a known status enum value.
        try:
            EntityStatus(transition.from_status)
            EntityStatus(transition.to_status)
        except ValueError:
            return False
        if not transition.provenance:
            return False
        return True

    def _commit_transition(self, entity: WorldEntity, transition: WorldTransition) -> None:
        entity.status = EntityStatus(transition.to_status)
        entity.version += 1
        entity.timestamp = transition.timestamp
        entity.provenance = list(transition.provenance)
        self._state.version += 1
        self._state.timestamp = transition.timestamp
        self._state.provenance = list(transition.provenance)

    # ---- relations ------------------------------------------------------
    def add_relation(self, relation: WorldRelation) -> None:
        if not relation.provenance:
            raise WorldModelError("relation requires provenance")
        self._relations[relation.relation_id] = relation
        self._state.relations[relation.relation_id] = relation
        if relation.source_entity in self._state.entities:
            self._state.entities[relation.source_entity].relations.append(relation.relation_id)

    # ---- snapshot / diff -----------------------------------------------
    def snapshot(self) -> WorldSnapshot:
        import copy

        snap = WorldSnapshot(
            version=self._state.version,
            entities=[copy.deepcopy(e) for e in self._state.entities.values()],
            relations=[copy.deepcopy(r) for r in self._state.relations.values()],
            provenance=list(self._state.provenance),
        )
        self._snapshots.append(snap)
        return snap

    def diff(self, a: WorldSnapshot, b: WorldSnapshot) -> dict[str, Any]:
        a_entities = {e.entity_id: e.status.value for e in a.entities}
        b_entities = {e.entity_id: e.status.value for e in b.entities}
        changed = {}
        for eid, st in b_entities.items():
            if a_entities.get(eid) != st:
                changed[eid] = {"from": a_entities.get(eid), "to": st}
        return {"changed_entities": changed, "added": set(b_entities) - set(a_entities)}

    # ---- introspection -------------------------------------------------
    @property
    def state(self) -> WorldState:
        return self._state

    def get_entity(self, entity_id: str) -> WorldEntity | None:
        return self._state.entities.get(entity_id)

    def history(self) -> list[WorldTransition]:
        return list(self._transitions)
