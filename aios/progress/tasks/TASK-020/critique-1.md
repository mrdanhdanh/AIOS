# TASK-020 — Critique 1

## Verdict: APPROVE

### Strengths
1. Clear upgrade flow: Resolve → Backup → Migrate → Validate → Rollback.
2. Dry-run requirement ensures no accidental side effects (AC-020-05, AC-020-06).
3. Rollback with evidence provides audit trail (AC-020-11).
4. Fail-closed: UNKNOWN compatibility not treated as compatible.

### Notes
1. Ensure migration engine checks Policy before executing mutations.
2. Backup should capture only necessary state, not entire filesystem.
3. Dry-run must be deterministic — same input produces same plan.

### Recommendation
APPROVE — proceed to second critique.
