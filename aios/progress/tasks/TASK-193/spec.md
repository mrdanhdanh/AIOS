# TASK-193 — Failure Attribution

## Objective
Triển khai Failure Attribution như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/failure_attribution.py` — class `FailureAttributor`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- Failure/AttributionReport immutable; attribute to known cause -> ATTRIBUTED; unknown cause -> UNKNOWN (never PASS); empty id/symptom raises EvaluationError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T186,T148,T147 (all DONE in prior milestones).
