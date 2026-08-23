# Breakdown — TASK-127

1. `aios/coder/generation.py` — `CodeGenerationRuntime` (thực thi CodingPlan T126).
2. `CapabilityDispatcher` Protocol — dispatch code op qua Capability (T009/T014, ARCH-004).
3. `GeneratedArtifact` — `content_hash` (sha256, T078) + `evidence_id` (T001 Rule 5).
4. Fail-closed: plan chưa VERIFIED / artifact không hash → `GenerationError` (T078).
5. Deterministic: cùng plan → cùng artifact set.
6. Tests (7) theo Test Matrix TASK-127 + architecture guard.
7. Tích hợp: T125/T126 -> T127 -> T128/T129 (M19).
