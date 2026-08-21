# TASK-024 — Context Optimizer

## Objective
Optimize context by relevance, budget, and lifecycle. Classifies context P0-P6, deduplicates, compresses deterministically, and enforces token budget.

## Deliverables
- `aios/context_optimizer/__init__.py`
- `aios/context_optimizer/contracts.py` — priority levels, context items
- `aios/context_optimizer/optimizer.py` — main optimizer
- `aios/context_optimizer/compressor.py` — deterministic compression
- `aios/context_optimizer/tests/` — tests

## Acceptance Criteria
- AC-024-01: Context classified P0–P6
- AC-024-02: Context doesn't exceed token budget
- AC-024-03: P0/P1 never dropped
- AC-024-04: Duplicates removed
- AC-024-05: Stale/expired handled
- AC-024-06: Deterministic compression before LLM
- AC-024-07: LLM compression optional + policy-gated
- AC-024-08: Provenance preserved after compression
- AC-024-09: INV-011/INV-012 enforced
- AC-024-10: Not dependent on specific Model Provider
- AC-024-11..17: Tests PASS

## Dependencies
- TASK-023 (Memory Coordinator)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
