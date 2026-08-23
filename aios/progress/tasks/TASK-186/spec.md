# TASK-186 — Evaluation Engine

## Objective
Triển khai Evaluation Engine như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/evaluation_engine.py` — class `EvaluationEngine`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- DimensionScore/ScoreReport immutable; score aggregates overall; PASS when all >= threshold; below-threshold -> INSUFFICIENT; empty -> UNKNOWN; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T185,T032,T078 (all DONE in prior milestones).
