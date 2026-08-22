# TASK-051 — Breakdown

## Steps
1. `aios/autonomous_planner/contracts.py` — AutonomousPlan, PlanTask, PlanStatus, ReplanTrigger, ReplanSafety.
2. `aios/autonomous_planner/validation.py` — PlanValidator (contract/dependency/capability/permission/policy/resource/risk/execution-graph).
3. `aios/autonomous_planner/planner.py` — AutonomousPlanner: deterministic-first `plan()`, `replan()`, `classify_replan_safety()`, context-aware validation.
4. `aios/autonomous_planner/tests/test_autonomous_planner.py` — 10 tests (unit/contract/integration/architecture).
5. Run architecture guard — no subprocess/provider/filesystem import in planner package.
6. Run full suite — no regressions.

## Exit Criteria
- All AC-051-01..08 PASS, gate PASS, no regressions.
