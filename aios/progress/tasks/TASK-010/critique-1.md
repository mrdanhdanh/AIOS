# TASK-010 — Critique 1 (Spec Review)

## Strengths
- Spec scopes Decision Pipeline correctly as deterministic-first control plane: Normalizer → RuleEngine → WorkflowMatcher → Planner → Policy → ExecutionPlan, with LLM only on INSUFFICIENT.
- Deliverables pin exact files (`normalizer.py`, `rule_engine.py`, `workflow_matcher.py`, `planner.py`, `execution_plan.py`, `decision_pipeline.py`) and keep governance backward compat.
- AC-010-01..10 mirror T010.md test matrix (deterministic no LLM, workflow reuse, planner fallback, validation, policy, offline, evidence, architecture, regression).
- Out-of-scope explicitly defers Goal/Worker/Tool/UI to later tasks.

## Risks / Gaps
- Normalizer alias map must be deterministic and cover T010.md examples (`run tests`, `system health`, `review project`, `create CRUD API`) without LLM.
- RuleEngine KNOWN_INTENTS must match Normalizer aliases; mismatch would cause deterministic requests to incorrectly escalate to LLM.
- WorkflowMatcher must be in-memory deterministic (substring/capability) and not require LLM or persistence.
- Planner validation pipeline must be fail-closed: empty/invalid output → REJECT, not silent fallback.
- ExecutionPlan must validate schema→contract→capability→permission→policy→resource before Runtime receives it.

## Required revisions
- [x] Lock alias map for 8+ intents (status/health/help/list_tasks/list_skills/review_code/diagnose_runtime/run_tests/create_crud_api) with deterministic fallback.
- [x] Define RuleEngine KNOWN_INTENTS aligned with Normalizer aliases.
- [x] Implement WorkflowLibrary in-memory with register/find_for_intent deterministic.
- [x] Implement Planner with validator + ExecutionPlan validation + capability registry check.
- [x] Implement ExecutionPlan with node/edge/permission/resource validation and cycle detection.

## Decision
- APPROVE with required revisions addressed — proceed to critique-2.
