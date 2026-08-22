# TASK-074 — Critique 1

## Strengths
- Reuses the existing `aios/upgrade` package (no parallel subsystem).
- Fail-closed verify gate is explicit and tested.
- Reversibility is enforced at plan-validation time (`is_fully_reversible`).
- Evidence is recorded per step (verify + apply + rollback) with content hashes.

## Risks / Gaps
- `aios/durable` (T066) named in the request does not exist in this workspace;
  the durable state is `aios/goal_durability`. Integration targets the real
  package to avoid a broken import.
- `verify` is a pre-apply applicability gate; post-state assertions belong in
  `up`/`down`, not in `verify` (otherwise the step can never apply).
- Determinism must exclude non-deterministic evidence metadata (run_id,
  timestamp) from equality checks.

## Required revisions
- Implement `MigrationPlan`/`MigrationEngine` with the exact contract fields.
- Provide a sample durable-state migration step with no data loss.
- Cover every AC and Test Matrix row with pytest tests; keep existing upgrade
  tests green.
