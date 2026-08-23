# TASK-196 — Continuous Evaluation

## Objective
Triển khai Continuous Evaluation như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/continuous_evaluation.py` — class `ContinuousEvaluation`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- ContinuousEvaluation.run integrates M25 components; ContinuousReport immutable; worst-of status; empty subject/None raises EvaluationError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T185,T186,T187,T188,T189,T190,T191,T192,T193,T194,T195,T021 (all DONE in prior milestones).
