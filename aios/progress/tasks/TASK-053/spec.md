# TASK-053 — Autonomous Loop

## Objective
Build a closed-loop autonomous control cycle: OBSERVE → ASSESS → PLAN → VALIDATE → ACT → OBSERVE → EVALUATE → LEARN → DECIDE (CONTINUE/REPLAN/WAIT/STOP). The loop *coordinates* existing primitives (T050/T051/T052/M5/M6); it never directly executes tools or runtime operations. All actions still flow through Policy, Permission, Runtime and Evidence.

## Scope
### In scope
- `AutonomousCycle` contract: cycle_id, goal_id, parent_cycle_id, world_state_ref, plan_ref, execution_ref, observation_ref, evaluation_ref, learning_ref, iteration, started_at, completed_at, status.
- Cycle status machine: CREATED/OBSERVING/PLANNING/VALIDATING/ACTING/EVALUATING/LEARNING/DECIDING/COMPLETED/REPLANNING/WAITING/STOPPED/FAILED.
- Observe: collect world-state delta from execution evidence + runtime events + artifacts + verification.
- Evaluate: goal progress, action success/failure, world-state change, policy violations, verification result, resource/cost, evidence completeness, replanning required (deterministic, Harness-first).
- Learn: candidate learning only, never auto-promoted (promotion belongs to T057).
- Re-plan: new version, no overwrite of plan history.
- Deterministic stop conditions: GOAL_COMPLETED/POLICY_DENIED/SAFETY_BLOCK/MAX_ITERATIONS/MAX_COST/MAX_RUNTIME/NO_PROGRESS/REPEATED_FAILURE/WORLD_STATE_INVALID/DEPENDENCY_BLOCKED/USER_STOP.

### Out of scope
- Policy/Permission enforcement (Governor T054), Recovery (T055), Memory promotion (T057), Evaluation decision layer (T060).

## Deliverables
- `aios/autonomous_loop/contracts.py` — AutonomousCycle, CycleStatus, Decision, StopCondition, CandidateLearning.
- `aios/autonomous_loop/loop.py` — LoopController/AutonomousLoop (orchestration, stop conditions).
- `aios/autonomous_loop/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-053-01: Cycle contract with all refs + status machine.
- AC-053-02: Loop coordinates OBSERVE→…→DECIDE without direct tool execution.
- AC-053-03: Evaluate uses deterministic evidence/Harness, not LLM verdict default.
- AC-053-04: Learning is candidate-only, not promoted.
- AC-053-05: Re-plan creates new version (no overwrite).
- AC-053-06: Deterministic stop conditions enforced (max_iterations/max_cost/no_progress/policy_denied).
- AC-053-07: No subprocess/provider/filesystem import (architecture gate).
- AC-053-08: Regression M0–M8 PASS.

## Dependencies
- TASK-050, TASK-051, TASK-052, M5, M6

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
