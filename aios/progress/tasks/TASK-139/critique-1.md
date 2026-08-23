# TASK-139 — Critique 1

## Missing / risky sections
- Runner phải dispatch qua `CapabilityDispatcher` Protocol (ARCH-004), không tự execute.
- `run` phải check `sandbox.is_usable` trước khi chạy (T136/T040).
- Policy deny -> raise fail-closed (T078).

## Risks
- Nếu chạy ngoài sandbox -> vi phạm T040.
- Nếu dispatcher BLOCKED mà không detect -> promote sai PASS.

## Verdict
SPEC acceptable; cần sandbox-only + fail-closed dispatch.
