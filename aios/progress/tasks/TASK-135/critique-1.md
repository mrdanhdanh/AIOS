# TASK-135 — Critique 1

## Missing / risky sections
- Spec thiếu định nghĩa rõ `CapabilityDispatcher` Protocol — cần làm rõ runner dispatch qua capability (ARCH-004).
- Cần đảm bảo `validate_request` enforce cả `sandbox_ref` và `policy_ref` (T136/T113 boundary).
- Provenance chain phải gắn `evidence_ref` (T001 Rule 5).

## Risks
- Nếu contract không fail-closed, execution sai có thể promote PASS (T078).
- Thiếu deterministic test -> regression khó phát hiện.

## Verdict
SPEC acceptable sau khi bổ sung Protocol + fail-closed validation.
