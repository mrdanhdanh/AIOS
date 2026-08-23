# TASK-024 Implementation — Context Optimizer

Implementation lives in `aios/context_optimizer/` (M5 Core Intelligence — Context Optimizer).

```
aios/context_optimizer/
  contracts.py   # ContextItem, ContextPriority (P0..P6), OptimizedContext, ContextBudget
  optimizer.py   # ContextOptimizer (deduplicate → compress → prioritize → budget)
  compressor.py  # DeterministicCompressor, ExtractiveCompressor, LLMCompressor
  __init__.py    # re-exports
  tests/
    test_optimizer.py
    test_compressor.py
    test_contracts.py
```

Priority: P0 System/Safety → P1 User Request → P2 Execution State → P3 Knowledge → P4 Memory → P5 Historical → P6 Optional. When budget insufficient, drops from P6 upward (never random truncation). Receives `MemoryContext` from TASK-023, not direct store access.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
