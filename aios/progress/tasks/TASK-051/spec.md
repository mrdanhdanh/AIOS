# TASK-051 — Autonomous Planner

## Objective
Build the **Autonomous Planner** — a dynamic, goal-level planning & re-planning layer for long-horizon goals. It extends the existing Planning Engine (M5) rather than creating a parallel planning system. Deterministic-first: existing workflow / known template / rule-based / previous valid plan adaptation are preferred over the LLM planner.

## Scope
### In scope
- `AutonomousPlan` contract: goal_id, plan_id, version, objective, tasks[], dependencies, assumptions, risks, required_capabilities, resource_estimate, policy_requirements, success_conditions, replan_conditions.
- Deterministic-first strategy ladder: EXISTING_WORKFLOW → KNOWN_TEMPLATE → RULE_BASED → PREVIOUS_PLAN → LLM_PLANNER (LLM never default).
- Dynamic re-planning triggered by task failure / dependency change / resource exhaustion / capability unavailable / policy change / execution deviation / invalid assumption / progress not met.
- Plan validation pipeline: contract → dependency → capability → permission → policy → resource → risk → execution-graph (DAG, no cycle). Invalid plan → REJECTED, never auto-executed.
- Re-plan safety classification: SAFE_TO_REPLAN / REPLAN_AFTER_CURRENT_TASK / REPLAN_AFTER_CHECKPOINT / REQUIRES_HUMAN_APPROVAL / BLOCKED.
- Plan compiles to existing Execution Graph (DAG). Planner owns planning only — not policy/permission/resource/execution/tool/credential/sandbox.

### Out of scope
- World Model (TASK-052), Autonomous Loop (TASK-053), Autonomy Governor (TASK-054), execution, policy enforcement.

## Deliverables
- `aios/autonomous_planner/contracts.py` — AutonomousPlan, PlanTask, PlanStatus, ReplanTrigger, ReplanSafety.
- `aios/autonomous_planner/planner.py` — AutonomousPlanner (plan, replan, classify_replan_safety, deterministic-first).
- `aios/autonomous_planner/validation.py` — PlanValidator (8-stage validation).
- `aios/autonomous_planner/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-051-01: Plan has full contract fields and is serializable.
- AC-051-02: Deterministic-first — no LLM call when workflow/template/rule/previous plan suffices.
- AC-051-03: LLM only used as fallback; call count tracked.
- AC-051-04: Plan validation rejects unknown capability / permission / policy / resource / cycle.
- AC-051-05: Re-plan creates a new version, supersedes previous plan (no overwrite).
- AC-051-06: Re-plan safety classified (policy change → REQUIRES_HUMAN_APPROVAL under supervised).
- AC-051-07: Planner does not import subprocess/provider/filesystem directly (architecture gate).
- AC-051-08: Regression of M0–M8 PASS.

## Dependencies
- TASK-050 Autonomous Goal Engine
- TASK-026 Planning Engine (M5)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
