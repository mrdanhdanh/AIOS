# TASK-130 Implementation

Coding Artifact + CodingEvidence lives in:

- `aios/coder/artifact.py` — `CodingArtifact`, `CodingArtifactRegistry`, `EvidenceLink`, `ArtifactKind`, `ArtifactStatus`, `ArtifactError`.
- Tests trong `aios/coder/tests/test_artifact.py` (8 tests, Test Matrix TASK-130).

Design:
- `CodingArtifact` chuẩn hóa 3 kind (CODE/PATCH/REVIEW), mọi artifact ghi `content_hash` (sha256, T078) + `evidence_chain` (T001 Rule 5).
- `CodingArtifactRegistry.create()` sinh `artifact_id` immutable (uuid, không tái sử dụng, T001 Rule 1).
- `verify()` — integrity gate fail-closed (T078): hash mismatch / thiếu evidence chain / policy reject → `ArtifactStatus.REJECTED`, không promote PASS. Deterministic: cùng artifact + verifier → cùng status.

Integration (import-level, no rewrite):
- `aios.coder.generation` (T127) / `aios.coder.patch` (T128) / `aios.coder.review` (T129) — artifact producers
- `aios.governance.evidence` (T001) / `aios.verification_integrity` (T078)
- `aios.coder.artifact` (T130) closes the M19 coding pipeline (T125→T130).
