# TASK-207 — Session Fork

## Objective
Triển khai Session Fork như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/session_fork.py` — class `SessionFork`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Session Fork implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- SessionFork.fork preserves parent artifacts into an isolated fork.
- Fork is fail-closed (illegal parent state raises CodingEditionError).
- fork_hash is content-addressed over the snapshot.
- UNKNOWN never promoted to PASS; evidence has provenance.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
