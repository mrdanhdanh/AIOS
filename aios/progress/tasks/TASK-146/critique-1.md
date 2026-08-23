# TASK-146 — Critique 1

## Missing / risky sections
- `observation_id` immutable (T001 Rule 1).
- Observation thiếu provenance → reject (fail-closed, T001 Rule 5).
- Cùng execution → cùng trace (deterministic, T135).
- Không lộ secret (T040/T113).

## Risks
- Nếu observation không yêu cầu evidence_ref → vi phạm T001 Rule 5.
- Nếu trace lộ secret → vi phạm T040/T113.

## Verdict
SPEC acceptable; cần fail-closed provenance + secret redaction + deterministic trace.
