# TASK-213 — Coding Health Score

## Objective
Triển khai Coding Health Score như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/health.py` — class `CodingHealthScore`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Coding Health Score implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- CodingHealthScore.compute returns weighted score in [0,1].
- Missing dimension or out-of-range score -> CodingEditionError.
- health_hash is content-addressed over the report.
- UNKNOWN never promoted to PASS; evidence has provenance.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
