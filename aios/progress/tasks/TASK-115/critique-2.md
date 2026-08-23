# Critique 2 — TASK-115

- **Phạm vi khớp detailtask/TASK-115.md:** Usage / Cost / Audit / Evidence được implement trong `aios/model_runtime/usage.py`.
- **Fail-closed:** mọi reject path (invalid contract / unresolved / timeout / inconclusive) raise đúng exception.
- **Deterministic:** cùng input + cùng state -> cùng output; LLM call count = 0 ở resolver.
- **Provenance:** mọi event/record mang provenance (T001 Rule 5); credential value không lộ (T040).
- **Tích hợp:** T112/T114 -> T115 -> T116 — import-level với Provider Registry / Model Registry / Identity / Security / Certification / Integrity.
- **Tests:** 6 scenario theo Test Matrix, all passing.
