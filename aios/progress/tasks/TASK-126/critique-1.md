# Critique 1 — TASK-126

## Missing / weak sections
- Spec cần làm rõ định nghĩa "rule đủ" vs "rule không đủ" — đã map qua `_KNOWN_INTENTS` (deterministic) vs `llm_fallback` (insufficient).
- Cần quy định rõ PlanVerifier reject điều gì: empty plan, thiếu mutating/test action, target không hợp lệ, policy reject.

## Risks
- Nếu verifier quá lỏng → plan sai được execute (vi phạm T078 fail-closed).
- Nếu verifier quá chặt → plan hợp lệ bị reject (false negative).

## Recommendations
- Verifier yêu cầu ít nhất 1 mutating action (create/patch/refactor) + 1 test action.
- Mọi plan phải có `evidence_id` + `content_hash` (T001 Rule 5).
- Test cover cả architecture (no forbidden imports).
