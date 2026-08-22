# TASK-056 — Long-Horizon Goal Execution & Durable Resume

## Objective
Build a **goal-level durability layer** so an autonomous goal survives many executions / workflows / sessions / restarts. On interruption the goal remains intact and continues *exactly* from the nearest safe point: authoritative state is restored, validity is *verified*, then execution continues without duplicating side effects, losing provenance, or re-running completed steps. This is a layer over the existing Runtime (StateStore / Executor / ExecutionGraph / AutonomousGoalEngine) — NOT a new checkpoint service or parallel subsystem.

## Scope
### In scope
- `DurableCheckpoint` contract: checkpoint_id, goal_id, sequence (monotonic, atomic), created_at, interruption_cause, goal_state, current_subgoal, completed_tasks[], pending_tasks[], execution_graph_state, world_state_ref, memory_refs[], artifact_refs[], policy_autonomy_state, recovery_state, evidence_refs[], content_hash.
- Checkpoint Coordinator: immutable, atomic, versioned commit via existing StateStore; `sequence` monotonic (old cannot overwrite new).
- Resume Validator: verify content_hash + provenance (evidence exists) + policy re-validation before resuming.
- Stale Detector: compare plan/world/policy versions; stale → re-plan (not blind continue).
- Idempotency Guard: completed-task set (no re-run) + side-effect action keys (no duplicate).
- Interruption taxonomy (6 causes) with per-cause resume strategy.
- SAFE-STOP for invalid / inconclusive checkpoints (fail-closed).
- Integration with T055 Recovery and T051 Re-plan.

### Out of scope
- New StateStore / Checkpoint Service (reuse M1), Memory store (T057), policy engine.

## Deliverables
- `aios/goal_durability/contracts.py` — DurableCheckpoint, InterruptionCause, ResumeVerdict.
- `aios/goal_durability/layer.py` — GoalDurabilityLayer (coordinator/validator/stale/idempotency/resume).
- `aios/goal_durability/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-056-01: Goal survives multiple executions/workflows/sessions intact.
- AC-056-02: DurableCheckpoint contains full semantics (§2).
- AC-056-03: Atomic commit + monotonic sequence (old does not overwrite new).
- AC-056-04: Resume does not re-run completed_tasks (idempotency).
- AC-056-05: Resume does not duplicate side effects (idempotency key).
- AC-056-06: 6 interruption causes distinguished with correct strategy.
- AC-056-07: Resume validates hash + provenance + policy; invalid/inconclusive → SAFE-STOP.
- AC-056-08: Stale checkpoint → re-plan, not blind continue.
- AC-056-09: No subprocess/provider/filesystem import (architecture gate).
- AC-056-10: Regression M0–M8 PASS.

## Dependencies
- TASK-055 Autonomous Recovery
- TASK-050 Autonomous Goal Engine
- TASK-005 State Service (M1)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
