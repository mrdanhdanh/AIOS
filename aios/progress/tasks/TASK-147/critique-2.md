# TASK-147 — Critique 2

## Missing / risky sections
- Mọi classification có provenance (T001 Rule 5).
- Confidence trong [0,1]; dưới threshold → UNKNOWN.

## Risks
- Nếu confidence ngoài [0,1] → invalid state.

## Verdict
SPEC acceptable; cần provenance + confidence guard.
