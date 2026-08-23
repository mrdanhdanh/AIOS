# TASK-208 — Multi-Agent Coding

## Objective
Triển khai Multi-Agent Coding như một năng lực có contract, evidence và harness riêng (M26 — AIOS 2.0 Coding Edition).

## Scope
- Package: `aios/coding_edition/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/coding_edition/multi_agent.py` — class `MultiAgentCoordinator`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Multi-Agent Coding implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- MultiAgentCoordinator assigns roles deterministically.
- detect_conflict finds two agents on the same task.
- coordinator_hash is content-addressed over assignments.
- UNKNOWN never promoted to PASS; evidence has provenance.

## Dependencies
- T125,T145,T177,T176,T183,T153,T102,T055,T130,T007,T034,T187,T180,T049,T195,T028,T119,T117,T021,T164 (all DONE in prior milestones).
