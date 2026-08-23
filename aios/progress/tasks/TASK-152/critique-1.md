# TASK-152 — Critique 1

## Missing / risky sections
- `chain_id` immutable (T001 Rule 1).
- Snapshot mismatch → reject (fail-closed, T137).
- Cùng state → cùng context (deterministic, T024).
- Chỉ chain output đã verify PASS (T078).

## Risks
- Nếu snapshot mismatch không reject → vi phạm T137.
- Nếu unverified output được chain → vi phạm T078.

## Verdict
SPEC acceptable; cần fail-closed snapshot + verified-only chain + deterministic context.
