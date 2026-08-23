# Critique 1 — TASK-132

## Missing / weak sections
- Spec cần làm rõ 3 autonomy level (SUPERVISED/ASSISTED/AUTONOMOUS) map tới tập operations nào (plan/review/generate/apply/patch).
- Cần quy định fail-closed: op không thuộc level → denied, không silent-allow (T113).

## Risks
- Nếu op denied mà vẫn thực thi → vi phạm T113.
- Nếu không ghi provenance → mất traceability (T001 Rule 5).

## Recommendations
- `AutonomyPermissionBroker.check()` fail-closed: op không trong level set / policy reject / unknown op → allowed=False.
- `require()` raise `PermissionError_` khi denied.
- Mọi `PermissionDecision` ghi `evidence_id` + `content_hash` (T001 Rule 5).
- Test cover architecture (no forbidden imports).
