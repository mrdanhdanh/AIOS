# TASK-149 — Critique 1

## Missing / risky sections
- `plan_id` immutable (T001 Rule 1).
- Mọi plan có rollback (T055) — fail → revert.
- Cùng diagnosis → cùng plan (deterministic).
- Plan không vượt policy boundary (T113).

## Risks
- Nếu plan thiếu rollback → vi phạm T055.
- Nếu UNKNOWN diagnosis được plan → vi phạm T078.

## Verdict
SPEC acceptable; cần fail-closed rollback + UNKNOWN reject + deterministic.
