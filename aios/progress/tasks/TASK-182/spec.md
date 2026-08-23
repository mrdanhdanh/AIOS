# TASK-182 — Trust Lifecycle + Invalidation + Selective Reverification

## Objective
Triển khai Trust Lifecycle + Invalidation + Selective Reverification như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/trust_lifecycle.py` — class `TrustLifecycle`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- TrustCertificate immutable; invalidate sets INVALID; reverify selective scopes; empty reason raises QualityGateError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T181,T164,T049,T046 (all DONE in prior milestones).
