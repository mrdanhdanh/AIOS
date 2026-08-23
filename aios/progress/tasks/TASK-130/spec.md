# TASK-130 — Coding Artifact + CodingEvidence

## Objective
Triển khai **Coding Artifact + CodingEvidence** (M19) như một năng lực có contract, evidence và harness riêng — chuẩn hóa coding artifact (code/patch/review) và evidence có provenance xuyên suốt pipeline T125→T129. TASK-130 là **artifact + evidence chuẩn, không phải pipeline mới** (dựa trên Code Generation T127 + Patch T128 + Review T129 + Evidence T001 Rule 5 + Integrity T078). Đây là task cuối của M19.

## Scope
**In scope:** `aios/coder/artifact.py` — `CodingArtifact`, `CodingArtifactRegistry`, `EvidenceLink`, `ArtifactKind`, `ArtifactStatus`, `ArtifactError`.
**Out of scope:** conformance harness (T131, M20).

## Deliverables
- `aios/coder/artifact.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_artifact.py`.
- Tích hợp: T125→T130 (M19 pipeline hoàn chỉnh).

## Acceptance Criteria
- Coding Artifact chuẩn hóa (code/patch/review) có `content_hash` (T078).
- Mọi artifact có provenance chain đầy đủ (T001 Rule 5).
- Artifact không verify → không promote PASS (fail-closed, T078).
- `artifact_id` immutable (T001 Rule 1).
- Cùng artifact + verifier → cùng verdict (deterministic).
- Tích hợp được với Generation + Patch + Review + Evidence + Integrity.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T125..T129 -> T130 (đóng M19).
- T001 (Rule 1/5), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
