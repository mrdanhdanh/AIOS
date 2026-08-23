# TASK-180 — Release Gate + Decision Explainability

## Objective
Triển khai Release Gate + Decision Explainability như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/release_gate.py` — class `ReleaseGate`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- ReleaseCriterion/ReleaseReport immutable; evaluate RELEASE/NO_RELEASE/BLOCKED with explanation; unmet blocking -> NO_RELEASE; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T175,T179,T181 (all DONE in prior milestones).
