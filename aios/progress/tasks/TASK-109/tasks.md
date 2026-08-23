# Breakdown — TASK-109

1. `aios/model_runtime/contracts.py` — `ModelContract, ModelRequest, ModelResponse, UsageSchema, CapabilityDeclaration, PolicyBoundary, validate_contract`.
2. Fail-closed guards (invalid/unresolved/timeout/inconclusive -> reject).
3. Deterministic path (rule engine, không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5).
5. Tích hợp dependency: T108 -> T109 -> T110/T111.
6. Tests (6) theo Test Matrix TASK-109.
