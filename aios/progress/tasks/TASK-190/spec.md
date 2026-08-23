# TASK-190 — Regression Detector

## Objective
Triển khai Regression Detector như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/regression_detector.py` — class `RegressionDetector`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- RegressionCheck/RegressionReport immutable; detect direction-aware (higher_is_better); regressed -> INSUFFICIENT; missing baseline -> UNKNOWN; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T189,T159,T033 (all DONE in prior milestones).
