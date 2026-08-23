# Breakdown — TASK-118

1. `aios/context/symbol_index.py` — `SymbolIndex, SymbolIndexResult, Symbol`.
2. Fail-closed guards (invalid/unhashable/cycle/inconclusive -> reject).
3. Deterministic path (không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5); secret isolation (T040/T113).
5. Tích hợp dependency: T117 -> T118 -> T120/T121.
6. Tests (6) theo Test Matrix TASK-118.
