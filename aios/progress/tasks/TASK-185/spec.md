# TASK-185 — Coding Evaluation Contract

## Objective
Triển khai Coding Evaluation Contract như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/evaluation_contract.py` — class `EvaluationContractValidator`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- EvaluationContract/ContractValidationReport immutable with non-empty ids; validate computes status PASS/UNKNOWN; empty dimensions -> UNKNOWN; invalid threshold raises EvaluationError; report_id deterministic (sha256).
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T032,T001 (all DONE in prior milestones).
