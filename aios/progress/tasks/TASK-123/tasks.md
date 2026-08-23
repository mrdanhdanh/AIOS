# Breakdown — TASK-123

1. `aios/context/verification.py` — `ContextVerification, VerificationResult, VerificationVerdict`.
2. Fail-closed guards (invalid/unhashable/cycle/inconclusive -> reject).
3. Deterministic path (không LLM; LLM call count = 0).
4. Provenance trên mọi event/record (T001 Rule 5); secret isolation (T040/T113).
5. Tích hợp dependency: T122 -> T123 -> T124.
6. Tests (6) theo Test Matrix TASK-123.
