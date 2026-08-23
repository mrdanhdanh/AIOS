# TASK-177 — Policy Engine + Profiles + Precedence

## Objective
Triển khai Policy Engine + Profiles + Precedence như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/policy_engine.py` — class `PolicyEngine`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- Policy/PolicyReport immutable; evaluate with profile + precedence; no match -> BLOCKED; precedence tie -> BLOCKED; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T176,T113,T138 (all DONE in prior milestones).
