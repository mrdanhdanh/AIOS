# TASK-145 — Critique 2

## Missing / risky sections
- Provenance trên mọi transition (T001 Rule 5).
- Transition history phải ghi đầy đủ (audit).
- Determinism: map state→next_state đóng.

## Risks
- Nếu history không ghi → không trace được chuỗi transition.
- Nếu map không đóng → non-deterministic.

## Verdict
SPEC acceptable sau critique 1; cần provenance + history + closed map.
