# TASK-235 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ conflict = 2 evidence cùng requirement, `status` mâu thuẫn (PASS vs FAIL), loại trừ UNKNOWN/STALE.
- Chưa chỉ định quality score = producer_trust × freshness × verification.

## Rủi ro
- Nếu evaluation nhận UNKNOWN/STALE → vi phạm "UNKNOWN ≠ PASS".

## Đề xuất
- `detect_conflicts()`, `replay(run_id)`, `quality_score()`, `is_valid_for_evaluation()`.
- Evaluation chỉ nhận evidence hợp lệ (non-UNKNOWN, non-STALE, non-conflict).
