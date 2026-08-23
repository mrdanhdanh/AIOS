# TASK-176 — Risk Model + Classification

## Objective
Triển khai Risk Model + Classification như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/risk_model.py` — class `RiskModel`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- RiskAsset/RiskReport immutable; classify from likelihood x impact; levels LOW/MEDIUM/HIGH/CRITICAL; invalid enum raises QualityGateError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T175,T164 (all DONE in prior milestones).
