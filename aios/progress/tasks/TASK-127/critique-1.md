# Critique 1 — TASK-127

## Missing / weak sections
- Spec cần làm rõ runtime chỉ dispatch qua Capability (T009/T014), không import `aios.tool`/runtime trực tiếp (ARCH-004).
- Cần quy định artifact không hash được → reject (fail-closed, T078).

## Risks
- Nếu runtime gọi tool trực tiếp → vi phạm ARCH-004.
- Nếu artifact không hash → mất integrity (T078).

## Recommendations
- `CodeGenerationRuntime` nhận `CapabilityDispatcher` (Protocol), không import tool.
- Mọi artifact ghi `content_hash` (sha256) + `evidence_id` (T001 Rule 5).
- Test cover architecture (no forbidden imports) + fail-closed (unhashable).
