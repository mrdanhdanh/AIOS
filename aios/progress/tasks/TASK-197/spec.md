# TASK-197 — Unified Coding Contract

## Objective
Triển khai Unified Coding Contract như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/contract.py` — class `CodingEditionContract`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Unified Coding Contract implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- CodingEditionContract is immutable and I/O-free (ARCH-001..004).
- contract_hash is deterministic (sha256 of inputs, no clock).
- verify_completion rejects non-prefix chains; empty id raises CodingEditionError.
- UNKNOWN never promoted to PASS; evidence has provenance; dependency regression PASS.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
