# TASK-147 — Critique 1

## Missing / risky sections
- `class_id` immutable (T001 Rule 1).
- UNKNOWN (confidence thấp) → không promote PASS (T078).
- Cùng observation → cùng class (deterministic).
- Taxonomy đóng — không sinh class ngoài tập.

## Risks
- Nếu UNKNOWN được promote → vi phạm T078.
- Nếu taxonomy không đóng → non-deterministic.

## Verdict
SPEC acceptable; cần fail-closed UNKNOWN + closed taxonomy + deterministic.
