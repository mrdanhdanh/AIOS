# TASK-181 — Governance Ledger + Provenance Graph

## Objective
Triển khai Governance Ledger + Provenance Graph như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/ledger.py` — class `GovernanceLedger`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- LedgerEntry immutable with entry_hash; record builds hash chain; verify detects tamper; ProvenanceGraph builds edges; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T180,T001,T078 (all DONE in prior milestones).
