# TASK-050 — Autonomous Goal Engine

## Objective
Build the Autonomous Goal Engine as the long-lived goal lifecycle/control substrate for M9. Manages goal identity/version, state persistence, objective/task tracking, progress observation, and goal state transitions (DRAFT→ACTIVE→PAUSED/BLOCKED→COMPLETED/FAILED/CANCELLED/EXPIRED) with evidence linkage. Goal Engine coordinates goal state — does not directly execute Tools.

## Scope
### In scope
- Goal contract: goal_id, version, owner/principal, tenant, title, description, objectives, constraints, priority, status, timestamps, provenance/evidence refs
- Goal state machine: DRAFT → ACTIVE → PAUSED/BLOCKED → COMPLETED/FAILED/CANCELLED/EXPIRED with valid transitions
- Objective model: Goal → Objectives → Tasks → Execution → Evidence → Verification
- Goal progress: completed/active/blocked/failed objectives with percentage, last_verified_at, evidence-backed (not just completed/total)
- Goal ↔ Execution linkage: Goal → Objective → Task → Execution → Graph → Events → Artifacts → Evidence → Verdict
- Goal decision boundary: Goal Engine decides goal state, Orchestrator decides task, Policy decides ALLOW/DENY (BLOCKED/ESCALATED on DENY, no bypass)
- Persistence: durable goal state (metadata, state, objectives, task/execution refs, progress, constraints, transitions, evidence)
- Goal events: GoalCreated, GoalActivated, GoalPaused, GoalResumed, GoalBlocked, GoalUnblocked, GoalProgressUpdated, GoalCompleted, GoalFailed, GoalCancelled, GoalExpired
- Integration with Orchestrator/Runtime via Policy/Capability/Tool chain

### Out of scope
- Autonomous Planner (TASK-051), World Model (052), Autonomous Loop (053), Autonomy Governor (054), etc. (M9 follow-up tasks)
- Creating a second Goal Manager (extends M2 Goal Manager)

## Deliverables
- `aios/autonomous_goal/contracts.py` — Goal, GoalPlan, GoalStatus
- `aios/autonomous_goal/engine.py` — AutonomousGoalEngine (create_goal, plan_goal, complete_goal, fail_goal, list_goals, get_goal, get_plan)
- `aios/autonomous_goal/tests/` — autonomous goal tests

## Acceptance Criteria
- AC-050-01: Goal has identity/version and is persistable
- AC-050-02: Goal state machine enforced (no arbitrary transitions)
- AC-050-03: Objective/task relationship tracked
- AC-050-04: Progress evidence-backed, not just ratio
- AC-050-05: Goal ↔ Execution linkage traceable
- AC-050-06: Goal decision boundary respected (no Policy bypass)
- AC-050-07: Persistence durable (not process memory only)
- AC-050-08: Goal events emitted on transitions
- AC-050-09: No Goal Engine → Tool/subprocess/filesystem/provider direct access
- AC-050-10: Regression M0–M8 PASS

## Dependencies
- TASK-049 — Certification

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
