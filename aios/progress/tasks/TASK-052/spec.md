# TASK-052 — World Model

## Objective
Build the **World Model** subsystem that represents the *current* state of the world/system AIOS acts upon, strictly separated from Memory. State is updated only through observations/evidence with provenance. No LLM is used as source of truth.

## Scope
### In scope
- Contracts: `WorldState`, `WorldEntity`, `WorldRelation`, `WorldObservation`, `WorldTransition`, `WorldSnapshot` — each with id/type/version/timestamp/source/provenance/confidence/status/scope.
- Entity model for Goal/Task/Workflow/Execution/Agent/Capability/Resource/Artifact/Workspace/Project/RuntimeNode/Environment/ExternalSystem with relations.
- Observation → Validate → Resolve Entity → Compare → Generate Transition → Validate → Commit.
- Snapshot + diff for replay/debug/recovery/comparison.
- Deterministic state transitions; LLM only as optional helper, never source of truth.

### Out of scope
- Memory store (TASK-007), Autonomous Planner execution, policy enforcement.

## Deliverables
- `aios/world_model/contracts.py` — World* contracts.
- `aios/world_model/engine.py` — WorldModel (observe, transition, snapshot, diff).
- `aios/world_model/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-052-01: WorldState/Entity/Relation/Observation/Transition/Snapshot contracts present with required fields.
- AC-052-02: Observation without provenance cannot become canonical state.
- AC-052-03: Observation → validated transition → committed new state, traceable to source observation.
- AC-052-04: Snapshot + diff supported.
- AC-052-05: World Model separated from Memory (no memory import as state store).
- AC-052-06: No subprocess/provider/filesystem import (architecture gate).
- AC-052-07: Regression M0–M8 PASS.

## Dependencies
- TASK-050 Autonomous Goal Engine
- TASK-051 Autonomous Planner

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
