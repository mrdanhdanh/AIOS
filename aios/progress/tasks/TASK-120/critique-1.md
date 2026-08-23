# Critique 1 — TASK-120

- **Phạm vi khớp detailtask/TASK-120.md:** Semantic + Hybrid Index được implement trong `aios/context/hybrid_index.py`.
- **Fail-closed:** mọi reject path (invalid / unhashable / cycle / inconclusive) raise đúng exception.
- **Deterministic:** cùng input + cùng state -> cùng output; LLM call count = 0.
- **Provenance:** mọi event/record mang provenance (T001 Rule 5); secret không lộ (T040).
- **Tích hợp:** T118/T119 -> T120 -> T121 — import-level với Evidence (T001) / Integrity (T078) / Security (T040/T113) / Context Optimizer (T024).
- **Tests:** 6 scenario theo Test Matrix, all passing.
