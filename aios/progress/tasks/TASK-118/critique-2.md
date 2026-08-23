# Critique 1 — TASK-118

- **Phạm vi khớp detailtask/TASK-118.md:** Source / Symbol Index được implement trong `aios/context/symbol_index.py`.
- **Fail-closed:** mọi reject path (invalid / unhashable / cycle / inconclusive) raise đúng exception.
- **Deterministic:** cùng input + cùng state -> cùng output; LLM call count = 0.
- **Provenance:** mọi event/record mang provenance (T001 Rule 5); secret không lộ (T040).
- **Tích hợp:** T117 -> T118 -> T120/T121 — import-level với Evidence (T001) / Integrity (T078) / Security (T040/T113) / Context Optimizer (T024).
- **Tests:** 6 scenario theo Test Matrix, all passing.
