# Breakdown — TASK-116

1. `aios/model_runtime/conformance.py` — `ConformanceSuite, ProviderCertifier, ProviderCertification, ConformanceResult`.
2. Fail-closed guards (invalid/unresolved/timeout/inconclusive -> reject).
3. Deterministic path (rule engine, không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5).
5. Tích hợp dependency: T110/T111/T112/T115 -> T116 -> T117 (M18).
6. Tests (6) theo Test Matrix TASK-116.
