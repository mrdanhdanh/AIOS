# Breakdown — TASK-117

1. `aios/context/scanner.py` — `RepositoryScanner, ScanResult, ScannedFile, ChangeSet, ScanError`.
2. Fail-closed guards (invalid/unhashable/cycle/inconclusive -> reject).
3. Deterministic path (không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5); secret isolation (T040/T113).
5. Tích hợp dependency: T116 -> T117 -> T118/T119.
6. Tests (6) theo Test Matrix TASK-117.
