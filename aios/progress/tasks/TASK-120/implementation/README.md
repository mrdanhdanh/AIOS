# TASK-120 Implementation

Semantic + Hybrid Index lives in:

- `aios/context/hybrid_index.py` — `HybridIndex, HybridIndexResult, HybridQueryResult, Embedding`.
- Tests trong `aios/context/tests/test_context.py` (Test Matrix TASK-120).

Integration (import-level, no rewrite):
- `aios.governance.evidence` (T001)
- `aios.verification_integrity` (T078)
- `aios.security` (T040/T113)
- `aios.context_optimizer` (T024)
- `aios.context.scanner` (T117) / `aios.context.symbol_index` (T118) / `aios.context.dependency_graph` (T119) / `aios.context.hybrid_index` (T120) / `aios.context.retriever` (T121) / `aios.context.builder` (T122) / `aios.context.verification` (T123) / `aios.context.conformance` (T124)
