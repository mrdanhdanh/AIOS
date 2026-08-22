# TASK-024 — Breakdown

## Steps
1. Create `aios/context_optimizer/contracts.py` — ContextPriority (P0-P6), ContextItem, ContextBudget, OptimizedContext contracts
2. Create `aios/context_optimizer/compressor.py` — DeterministicCompressor (dedup, merge, lifecycle filter)
3. Create `aios/context_optimizer/optimizer.py` — ContextOptimizer pipeline: Normalize → Deduplicate → Lifecycle Filter → Priority Assignment → Token Estimation → Budget Allocation → Deterministic/Extractive/LLM Compression → Validation
4. Implement P0-P6 priority enforcement (P0/P1 never dropped, drop from P6 upward)
5. Implement token budget enforcement (`final_tokens + reserve ≤ max_tokens`)
6. Implement provenance preservation through compression
7. Create `aios/context_optimizer/tests/test_optimizer.py` — 21 tests (priority, budget, dedup, lifecycle, compression, provenance, INV-011/012)
8. Run architecture guard — verify no `Agent → Memory Store` bypass, no Runtime/Provider direct imports
9. Run full suite — 1670/1670 PASS, no regressions

## Dependencies
- TASK-023 Memory Coordinator (MemoryContext input)

## Exit Criteria
- All AC-024-01..11 PASS, gate PASS, 1670 tests green
