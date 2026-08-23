# TASK-140 — Critique 1

## Missing / risky sections
- Runner phải dispatch qua `CapabilityDispatcher` Protocol (ARCH-004).
- `run` phải check `sandbox.is_usable` (T136/T040) + policy enforce (T138).
- Build + Lint result đều phải có `content_hash` (T078).

## Risks
- Nếu chạy ngoài sandbox -> vi phạm T040.
- Nếu dispatcher BLOCKED mà không detect -> promote sai PASS.

## Verdict
SPEC acceptable; cần sandbox-only + fail-closed dispatch.
