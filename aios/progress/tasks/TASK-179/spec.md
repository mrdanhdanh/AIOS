# TASK-179 — Quality Debt Tracking

## Objective
Triển khai Quality Debt Tracking như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/quality_debt.py` — class `QualityDebtTracker`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- DebtItem/DebtReport immutable; track classifies HEALTHY/AT_RISK/BREACH by critical count; invalid severity/negative age raises QualityGateError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T178,T175,T021 (all DONE in prior milestones).
