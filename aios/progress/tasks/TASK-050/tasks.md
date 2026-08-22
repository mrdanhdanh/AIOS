# TASK-050 — Breakdown

## Steps
1. Create `aios/autonomous_goal/contracts.py` — Goal (goal_id, title, description, status, priority, created_at), GoalPlan (plan_id, goal_id, steps, estimated_effort), GoalStatus (CREATED/PLANNING/EXECUTING/COMPLETED/FAILED/PAUSED)
2. Create `aios/autonomous_goal/engine.py` — AutonomousGoalEngine: create_goal, plan_goal (CREATED→PLANNING→EXECUTING), complete_goal (→COMPLETED), fail_goal (→FAILED), list_goals, get_goal, get_plan
3. Implement goal state machine with valid transitions and persistence
4. Implement objective/task tracking and progress with evidence linkage
5. Implement goal decision boundary (no Policy bypass)
6. Create `aios/autonomous_goal/tests/` — 7 tests (create, plan, complete, fail, list, get, state transitions)
7. Run architecture guard — verify no Goal Engine → Tool/subprocess/filesystem/provider
8. Run full suite — 1840/1840 PASS (7 new), no regressions

## Dependencies
- TASK-049 Certification

## Exit Criteria
- All AC-050-01..10 PASS, gate PASS, no regressions
