# TASK-127 Implementation

Code Generation Runtime lives in:

- `aios/coder/generation.py` — `CodeGenerationRuntime`, `GenerationRun`, `GeneratedArtifact`, `CapabilityDispatcher`, `GenerationStatus`, `GenerationError`.
- Tests trong `aios/coder/tests/test_generation.py` (7 tests, Test Matrix TASK-127).

Design:
- `CodeGenerationRuntime.run(plan)` — thực thi CodingPlan đã VERIFIED (T126) thành `GeneratedArtifact` qua `CapabilityDispatcher` (Protocol, T009/T014). Không import `aios.tool`/runtime trực tiếp (ARCH-004).
- Mỗi artifact ghi `content_hash` (sha256, T078) + `evidence_id` (T001 Rule 5).
- Fail-closed: plan chưa VERIFIED hoặc capability trả non-string → `GenerationError` (T078).
- Deterministic: cùng plan → cùng artifact set (tested).

Integration (import-level, no rewrite):
- `aios.coder.contract` (T125) — agent boundary
- `aios.coder.planner` (T126) — plan input
- `aios.governance.evidence` (T001) / `aios.verification_integrity` (T078)
- `aios.capability` (T009/T014) — dispatch boundary
- `aios.coder.generation` (T127) -> `aios.coder.patch` (T128) / `aios.coder.review` (T129)
