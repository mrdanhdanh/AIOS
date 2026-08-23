# TASK-023 Implementation — Memory Coordinator

Implementation lives in `aios/memory_coordinator/` (M5 Core Intelligence — Memory Coordinator).

```
aios/memory_coordinator/
  contracts.py   # MemoryQuery, MemoryCandidate, MemoryScore, MemorySelection, MemoryContext, MemoryType
  coordinator.py # MemoryCoordinator (unified retrieval from 4 stores)
  filter.py      # Filtering by execution/request context, scope, provenance
  ranker.py      # Deterministic ranking
  dedup.py       # Deduplication
  __init__.py    # re-exports
  tests/
    test_coordinator.py
    test_filter.py
    test_ranker.py
    test_dedup.py
```

Pipeline: `Memory Stores → Coordinator → Retrieve → Filter → Rank → Deduplicate → Compress → Prioritize → MemoryContext → Context Service`. Four sources: Conversation/Session/Knowledge/Artifact memory. Isolation and provenance preserved.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
