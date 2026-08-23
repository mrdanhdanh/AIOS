# Critique 1 — TASK-129

## Missing / weak sections
- Spec cần làm rõ review agent là pure function (I/O-free), chỉ đề xuất verdict, không tự apply/patch (T022 no God Object).
- Cần quy định finding BLOCK → verdict BLOCK (fail-closed, T078).

## Risks
- Nếu agent bypass policy → vi phạm T022/T113.
- Nếu không fail-closed → finding block mà vẫn APPROVE.

## Recommendations
- `CodeReviewAgent.review()` pure: nhận content, trả `ReviewReport`; `policy_ok=False` → `ReviewError`.
- BLOCK finding → `Verdict.BLOCK`; mọi finding ghi `evidence_id` (T001 Rule 5).
- Test cover architecture (no forbidden imports) + deterministic.
