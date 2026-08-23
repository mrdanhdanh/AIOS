# TASK-175 — Quality Gate + Gate States

## Objective
Triển khai Quality Gate + Gate States như một năng lực có contract, evidence và harness riêng (M24 — Governance & Quality).

## Scope
- Package: `aios/quality_gate/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/quality_gate/gate_states.py` — class `QualityGate`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- QualityGate state machine; GateCheck/GateReport immutable with non-empty ids; evaluate computes state PASS/FAIL/UNKNOWN; UNKNOWN never promoted to PASS; empty checks -> UNKNOWN; report_id deterministic (sha256).
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T164,T151,T001 (all DONE in prior milestones).
