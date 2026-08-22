# TASK-026 — Breakdown

## Steps
1. Create `aios/planning_engine/contracts.py` — Goal, PlannedTask, ExecutionPlan, RiskLevel contracts
2. Create `aios/planning_engine/planner.py` — PlanningEngine pipeline: Goal Analyzer → Task Decomposer → Dependency Analyzer → Capability Resolver → Risk Analyzer → Execution Planner → Plan Validator
3. Implement deterministic-first planning (Known Workflow → Template → Rule → LLM fallback), cycle detection, plan validation (INV-014)
4. Implement capability resolution via Capability Registry (not direct Tool selection), resource estimation, risk analysis
5. Create `aios/planning_engine/tests/test_planner.py` — 12 tests (goal analysis, decomposition, dependency, capability, validation, cycle detection)
6. Run architecture guard — verify no Planner → Tool/subprocess/filesystem direct access
7. Run full suite — 1693/1693 PASS (12 new), no regressions

## Dependencies
- TASK-025 Model Router

## Exit Criteria
- All AC-026 PASS, gate PASS, no regressions
