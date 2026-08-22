# TASK-062 — Autonomous Scheduler

## Objective
Build a **scheduler layer** for the Autonomous Goal that activates a goal / workflow according to a schedule (cron) or trigger (event / manual) in an **autonomy-aware and fail-closed** way. TASK-062 is the **activation / orchestration trigger**, not the goal engine, planner, or execution loop.

## Scope
### In scope
- `ScheduleEntry` (goal_id, trigger: CRON|EVENT|MANUAL, cron_expr/event_filter/manual_token, autonomy_level_required, enabled, next_fire derived).
- `TriggerType` enum (CRON / EVENT / MANUAL).
- **Schedule Registry** — durable store of schedule/trigger per goal (persist across restart, designed for T066 Durable Execution).
- **Trigger Engine** — evaluate cron / event / manual trigger.
- **Activation Policy** — check autonomy level, resource budget, policy before activate.
- **Scheduler Gate** — activate only when Governor (T054) authorizes.
- Fail-closed: undefined / non-matching trigger → NO activate.
- Deterministic: same trigger state + policy version → same activate decision.
- Audit evidence per activation (who triggered, when, which policy).

### Out of scope
- Goal engine (T050), Planner (T051), Autonomous Loop (T053), Governor (T054), Stuck Detection (T061), Recovery (T055).

## Deliverables
- `aios/autonomous_scheduler/contracts.py` — ScheduleEntry, TriggerType.
- `aios/autonomous_scheduler/scheduler.py` — Scheduler (registry + trigger engine + activation policy), SchedulerGate.
- `aios/autonomous_scheduler/tests/test_autonomous_scheduler.py` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-062-01: Goal activates only with a valid schedule/trigger.
- AC-062-02: Schedule ≠ Plan ≠ Execute (Scheduler triggers, Planner/Goal define content, Governor decides permission).
- AC-062-03: Cron trigger due → activate (via Governor).
- AC-062-04: Event trigger matches filter → activate (via Governor).
- AC-062-05: Manual trigger with valid token → activate.
- AC-062-06: Undefined / non-matching trigger → NO activate (fail-closed).
- AC-062-07: Activation respects autonomy level (budget exceeded → BLOCK).
- AC-062-08: Each activation records audit evidence (full provenance).
- AC-062-09: Schedule durable (persist across restart).
- AC-062-10: Scheduler deterministic (same trigger state + policy version → same decision).
- AC-062-11: Integrates with Goal Engine (T050) + Planner (T051) + Loop (T053).
- AC-062-12: No second autonomous control plane.
- AC-062-13: Regression M0–M8 PASS; no architecture invariant violation.

## Dependencies
- TASK-050 Autonomous Goal Engine, TASK-051 Autonomous Planner, TASK-053 Autonomous Loop, TASK-054 Autonomy Governor

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
