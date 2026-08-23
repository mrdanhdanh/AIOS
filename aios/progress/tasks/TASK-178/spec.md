# TASK-178 — Exception Management

## Objective
Triển khai Exception Management như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/exception_management.py` — class `ExceptionManager`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- ExceptionRequest/ExceptionReport immutable; request approves when justified, REJECTED without justification (fail-closed); report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T177,T097,T055 (all DONE in prior milestones).
