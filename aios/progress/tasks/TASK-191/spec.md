# TASK-191 — Agent Behavior Evaluator

## Objective
Triển khai Agent Behavior Evaluator như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/agent_behavior_evaluator.py` — class `AgentBehaviorEvaluator`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- BehaviorSpec/BehaviorEvalReport immutable; evaluate expected==actual; mismatch -> INSUFFICIENT; empty id raises EvaluationError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T186,T157,T187 (all DONE in prior milestones).
