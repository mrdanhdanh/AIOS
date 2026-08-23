# TASK-195 — Model / Agent Benchmark

## Objective
Triển khai Model / Agent Benchmark như một năng lực có contract, evidence và harness riêng (M25 — Evaluation & Benchmark).

## Scope
- Package: `aios/evaluation/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/evaluation/model_agent_benchmark.py` — class `ModelAgentBenchmark`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- BenchmarkResult/BenchmarkReport immutable; run suite; BREACH -> INSUFFICIENT; UNKNOWN -> UNKNOWN; else PASS; invalid status raises EvaluationError; report_id deterministic.
- UNKNOWN không được nâng thành PASS; evidence có provenance; regression của dependency PASS.

## Dependencies
- T188,T189,T186 (all DONE in prior milestones).
