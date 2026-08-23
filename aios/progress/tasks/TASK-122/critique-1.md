# Critique 1 — TASK-122

- **Phạm vi khớp detailtask/TASK-122.md:** Context Builder + Budget được implement trong `aios/context/builder.py`.
- **Fail-closed:** mọi reject path (invalid / unhashable / cycle / inconclusive) raise đúng exception.
- **Deterministic:** cùng input + cùng state -> cùng output; LLM call count = 0.
- **Provenance:** mọi event/record mang provenance (T001 Rule 5); secret không lộ (T040).
- **Tích hợp:** T121 -> T122 -> T123 — import-level với Evidence (T001) / Integrity (T078) / Security (T040/T113) / Context Optimizer (T024).
- **Tests:** 6 scenario theo Test Matrix, all passing.
