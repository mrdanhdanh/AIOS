# Breakdown — TASK-130

1. `aios/coder/artifact.py` — `CodingArtifact` (3 kind: code/patch/review) + `content_hash` (T078).
2. `EvidenceLink` + `evidence_chain` (provenance xuyên suốt T125→T129, T001 Rule 5).
3. `CodingArtifactRegistry` — `artifact_id` immutable (T001 Rule 1).
4. Integrity gate `verify()` fail-closed: hash mismatch / thiếu evidence / policy reject → REJECTED (T078/T113).
5. Deterministic: cùng artifact + verifier → cùng status.
6. Tests (8) theo Test Matrix TASK-130 + architecture guard.
7. Tích hợp: T125→T130 (M19 pipeline hoàn chỉnh).
