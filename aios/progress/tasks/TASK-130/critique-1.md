# Critique 1 — TASK-130

## Missing / weak sections
- Spec cần làm rõ artifact chuẩn hóa 3 kind (code/patch/review) đều có `content_hash` (T078).
- Cần quy định integrity gate fail-closed: artifact không verify → không promote PASS (T078).

## Risks
- Nếu artifact không verify mà vẫn PASS → vi phạm T078.
- Nếu `artifact_id` tái sử dụng → vi phạm T001 Rule 1.

## Recommendations
- `CodingArtifactRegistry.create()` sinh `artifact_id` immutable (uuid); `verify()` fail-closed (REJECTED khi hash mismatch / thiếu evidence / policy reject).
- Mọi artifact ghi `evidence_chain` (T001 Rule 5).
- Test cover fail-closed + immutable id + architecture.
