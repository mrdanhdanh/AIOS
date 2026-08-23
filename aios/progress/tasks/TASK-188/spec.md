# TASK-188 — Benchmark Registry

## Objective
Triển khai Benchmark Registry như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/benchmark_registry.py` — class `BenchmarkRegistry`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- Benchmark/RegistryReport immutable; register/lookup; duplicate id raises EvaluationError; unknown lookup -> UNKNOWN; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T187,T033,T185 (all DONE in prior milestones).
