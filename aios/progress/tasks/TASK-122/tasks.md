# Breakdown — TASK-122

1. `aios/context/builder.py` — `ContextBuilder, BuiltContext, BuiltChunk`.
2. Fail-closed guards (invalid/unhashable/cycle/inconclusive -> reject).
3. Deterministic path (không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5); secret isolation (T040/T113).
5. Tích hợp dependency: T121 -> T122 -> T123.
6. Tests (6) theo Test Matrix TASK-122.
