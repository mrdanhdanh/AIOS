# TASK-200 — Risk Engine

## Objective
Triển khai Risk Engine như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/risk.py` — class `RiskEngine`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Risk Engine implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- RiskEngine.assess returns weighted score in [0,1] and a band.
- Bands: LOW<0.25<=MEDIUM<0.5<=HIGH<0.75<=CRITICAL.
- No model -> UNKNOWN band; signal severity must be in [0,1].
- UNKNOWN never promoted to PASS; evidence has provenance.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
