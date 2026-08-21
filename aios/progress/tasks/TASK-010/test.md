# TASK-010 — Test Report

## Suites

| Suite | File | Cases | Result |
|-------|------|-------|--------|
| normalizer | `aios/orchestrator/tests/test_normalizer.py` | 12 | PASS |
| rule engine | `aios/orchestrator/tests/test_rule_engine.py` | 5 | PASS |
| workflow matcher | `aios/orchestrator/tests/test_workflow_matcher.py` | 8 | PASS |
| execution plan | `aios/orchestrator/tests/test_execution_plan.py` | 9 | PASS |
| planner | `aios/orchestrator/tests/test_planner.py` | 6 | PASS |
| decision pipeline | `aios/orchestrator/tests/test_decision_pipeline.py` | 13 | PASS |
| orchestrator architecture | `aios/orchestrator/tests/test_architecture.py` | 4 | PASS |
| governance deterministic | `aios/governance/deterministic/tests/test_deterministic.py` | 4 | PASS |
| full harness | `python -m pytest aios -q` | 601 | PASS |

## Coverage

- Normalizer: alias map deterministic, same semantic → stable intent, target/mode/priority/source_channel, governance Request compat.
- RuleEngine: 8 known intents SUFFICIENT with plan, unknown INSUFFICIENT, is_sufficient helper.
- WorkflowMatcher: WorkflowLibrary register/find (token overlap), duplicate/empty reject, SUFFICIENT passthrough, INSUFFICIENT→SUFFICIENT via workflow, NO_MATCH, match_intent helper.
- ExecutionPlan: valid plan, empty/duplicate/cycle/permission/resource/self-loop rejects, to_dict.
- Planner: LLM callable, empty/validator reject, JSON output, capability registry check (fail-closed when registry non-empty).
- DecisionPipeline: deterministic no LLM, workflow reuse no planner, planner fallback only when Rule=INSUFFICIENT AND Workflow=NO_MATCH, planner not called when rule/workflow sufficient, validation reject, policy DENY/ALLOW, offline deterministic, offline insufficient no planner raises, evidence chain, governance Request compat.
- Architecture: orchestrator does not import agents, does not import tool providers, planner does not execute tool, guard ARCH-004 clean.
- `python -m pytest aios -q` — 601 passed, 0 failed.

## AC mapping

| AC | Cases | Result |
|----|-------|--------|
| AC-010-01 normalization | test_normalizer (12) | PASS |
| AC-010-02 deterministic routing | test_rule_engine + test_decision_pipeline::test_deterministic_no_llm | PASS |
| AC-010-03 workflow reuse | test_workflow_matcher + test_decision_pipeline::test_workflow_reuse_no_planner | PASS |
| AC-010-04 planner fallback | test_planner + test_decision_pipeline::test_planner_fallback_only_when_needed | PASS |
| AC-010-05 planner validation | test_planner::test_planner_validator_reject + test_execution_plan | PASS |
| AC-010-06 policy boundary | test_decision_pipeline::test_policy_boundary/allow | PASS |
| AC-010-07 offline | test_decision_pipeline::test_offline_deterministic | PASS |
| AC-010-08 evidence | test_decision_pipeline::test_evidence_chain/planner | PASS |
| AC-010-09 architecture | test_architecture (4) | PASS |
| AC-010-10 regression | full harness 601 | PASS |
