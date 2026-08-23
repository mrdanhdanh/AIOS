# TASK-217 — AIOS 2.0 Coding Integration

## Objective
Triển khai AIOS 2.0 Coding Integration như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/integration.py` — class `CodingEdition`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- AIOS 2.0 Coding Integration implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- CodingEdition wires all 22 M26 components into one facade.
- run() drives the completion chain AUTHORIZED..CERTIFIED (fail-closed).
- integration_hash is content-addressed over the report.
- UNKNOWN never promoted to PASS; evidence has provenance.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
