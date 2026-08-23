# Critique 1 — TASK-133

## Missing / weak sections
- Spec cần làm rõ versioning: mỗi (template_id, version) immutable (T001 Rule 1); duplicate → reject.
- Cần quy định build fail-closed: missing variable / unresolved placeholder → reject (T078).

## Risks
- Nếu version tái sử dụng → vi phạm T001 Rule 1.
- Nếu placeholder chưa resolve mà vẫn trả prompt → vi phạm T078.

## Recommendations
- `PromptRegistry.register()` reject duplicate (template_id, version).
- `PromptBuilder.build()` fail-closed: missing variable / unresolved placeholder → `PromptError` (T078).
- Mọi `BuiltPrompt` ghi `evidence_id` + `content_hash` (T001 Rule 5).
- Test cover architecture (no forbidden imports).
