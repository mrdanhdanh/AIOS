# TASK-127 — Code Generation Runtime

## Objective
Triển khai **Code Generation Runtime** (M19) như một năng lực có contract, evidence và harness riêng — thực thi coding plan (T126) thành code artifact qua capability, không để agent truy cập tool/runtime trực tiếp. TASK-127 là **generation runtime, không phải agent mới** (dựa trên Coder Agent T125 + Coding Planner T126 + Worker T013 + Capability T009/T014).

## Scope
**In scope:** `aios/coder/generation.py` — `CodeGenerationRuntime`, `GenerationRun`, `GeneratedArtifact`, `CapabilityDispatcher`, `GenerationStatus`, `GenerationError`.
**Out of scope:** patch engine (T128); review agent (T129).

## Deliverables
- `aios/coder/generation.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_generation.py`.
- Tích hợp: T125/T126 -> T127 -> T128/T129 (M19).

## Acceptance Criteria
- Runtime thực thi CodingPlan (T126) thành code artifact.
- Agent không gọi tool/runtime trực tiếp (ARCH-004) → BLOCK.
- Mọi artifact có `content_hash` (T078) + provenance (T001 Rule 5).
- Artifact không hash được → reject (fail-closed, T078).
- Cùng plan → cùng artifact set (deterministic).
- Tích hợp được với Coder Agent + Planner + Capability + Worker + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T125 (Coder Agent), T126 (Planner) -> T127 -> T128/T129.
- T001 (Rule 5), T009/T014 (Capability), T013 (Worker), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
