# Critique 1 — TASK-131

## Missing / weak sections
- Spec cần làm rõ harness validate invariants nào: content_hash khớp, evidence_present, integrity_verified, producer authorized, no forbidden ops.
- Cần quy định UNKNOWN không promote PASS (fail-closed, T078).

## Risks
- Nếu UNKNOWN promote PASS → vi phạm T078.
- Nếu producer unauthorized mà vẫn PASS → vi phạm security (T113).

## Recommendations
- `CoderConformanceHarness.check()` fail-closed: mọi invariant thiếu → FAIL; security DENIED → FAIL.
- `promote()` trả False cho UNKNOWN/FAIL.
- Mọi `ConformanceResult` ghi `evidence_id` + `content_hash` (T001 Rule 5).
- Test cover architecture (no forbidden imports).
