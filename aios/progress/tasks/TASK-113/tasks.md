# Breakdown — TASK-113

1. `aios/model_runtime/security.py` — `SecurityGate, SecurityContext, CredentialBoundary, PermissionCheck, PolicyPrecheck`.
2. Fail-closed guards (invalid/unresolved/timeout/inconclusive -> reject).
3. Deterministic path (rule engine, không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5).
5. Tích hợp dependency: T112 -> T113 -> T114/T115.
6. Tests (6) theo Test Matrix TASK-113.
