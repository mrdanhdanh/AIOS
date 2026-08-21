# TASK-010 — Breakdown

- [x] **10.1** Create `aios/progress/tasks/TASK-010/` scaffold — `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`, `review.md`.
- [x] **10.2** Implement `aios/orchestrator/normalizer.py` — `NormalizedRequest`, `Normalizer` with alias map, target/mode/priority resolution, deterministic.
- [x] **10.3** Implement `aios/orchestrator/rule_engine.py` — `RuleDecision`, `RuleEngine` with KNOWN_INTENTS, SUFFICIENT/INSUFFICIENT, plan generation.
- [x] **10.4** Implement `aios/orchestrator/workflow_matcher.py` — `WorkflowLibrary`, `WorkflowMatcher` with in-memory deterministic matching.
- [x] **10.5** Implement `aios/orchestrator/execution_plan.py` — `PlanNode`, `PlanEdge`, `ExecutionPlan` with validation (schema, permissions, resources, cycle).
- [x] **10.6** Implement `aios/orchestrator/planner.py` — `PlannerRequest/Response`, `Planner` with LLM callable, validator, capability check, fail-closed.
- [x] **10.7** Implement `aios/orchestrator/decision_pipeline.py` — `DecisionPipeline`, `DecisionResult`, `DecisionEvidence` orchestrating full pipeline with evidence chain.
- [x] **10.8** Enhance `aios/governance/deterministic/pipeline.py` — keep backward compat, delegate to orchestrator where needed.
- [x] **10.9** Create `aios/orchestrator/tests/` — 7 test files covering AC-010-01..10 (≥40 tests).
- [x] **10.10** Run `python -m pytest aios -q` — verify 544+ tests PASS, no architecture violations.
- [x] **10.11** Write `test.md` + `evaluation.md` + `REGRESSION.md` with evidence.
- [x] **10.12** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-010 DONE.
