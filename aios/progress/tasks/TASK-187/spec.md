# TASK-187 — Quality Dimensions

## Objective
Triển khai Quality Dimensions như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/quality_dimensions.py` — class `QualityDimensionEvaluator`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- QualityDimension/DimensionReport immutable; evaluate value vs threshold; PASS/INSUFFICIENT; invalid weight/value raises EvaluationError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T186,T185 (all DONE in prior milestones).
