# TASK-203 — Safe Stop / Resume

## Objective
Triển khai Safe Stop / Resume như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/safe_stop.py` — class `SafeStopController`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Safe Stop / Resume implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- SafeStopController pauses with an immutable checkpoint and resumes.
- pause/resume are fail-closed (illegal state raises CodingEditionError).
- checkpoint_hash is content-addressed over all checkpoints.
- UNKNOWN never promoted to PASS; evidence has provenance.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
