# TASK-194 — Evaluation Store

## Objective
Triển khai Evaluation Store như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/evaluation_store.py` — class `EvaluationStore`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- StoredEvaluation/StoreReport immutable; store with content_hash; tamper -> EvaluationError/INSUFFICIENT; empty id/hash raises EvaluationError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T186,T185,T163,T001 (all DONE in prior milestones).
