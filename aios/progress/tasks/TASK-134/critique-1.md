# Critique 1 — TASK-134

## Missing / weak sections
- Spec cần làm rõ scope enforcement: resolve path thực tế (realpath) để bắt symlink escape; traversal/absolute-outside → DENIED.
- Cần quy định fail-closed: escape → DENIED, không silent-allow (T113).

## Risks
- Nếu path escape mà vẫn ALLOWED → vi phạm security boundary (T113).
- Nếu không ghi provenance → mất traceability (T001 Rule 5).

## Recommendations
- `FileSafetyBoundary.check()` resolve realpath; escape → DENIED. `require()` raise.
- Scope root phải tồn tại (constructor reject nếu không).
- Mọi `ScopeDecision` ghi `evidence_id` + `content_hash` (T001 Rule 5).
- Test cover architecture (no forbidden imports beyond os).
