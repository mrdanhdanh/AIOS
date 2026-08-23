# TASK-184 — Quality Dashboard + Governance Harness

## Objective
Triển khai Quality Dashboard + Governance Harness như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/dashboard.py` — class `GovernanceHarness`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- QualityDashboard.aggregate + GovernanceHarness.run integrate M24 components; immutable reports; empty subject/None raises QualityGateError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T175,T176,T177,T178,T179,T180,T181,T182,T183,T072,T021 (all DONE in prior milestones).
