# TASK-074 — Upgrade & Migration 1.0

## Objective
Build **Upgrade & Migration 1.0** — a safe, reversible, evidence-backed
mechanism to upgrade AIOS and migrate state/data between versions. This is
**migration tooling**, not a runtime feature. It extends the existing
`aios/upgrade` package and integrates with the durable state layer
(`aios/goal_durability`, the T066-equivalent durable layer present in this
workspace) and the T032 verification harness (`aios/harness/verification`).

## Scope
**In scope**
- `MigrationPlan` dataclass: `from_version`, `to_version`, `steps` (list of
  `{id, up, down, verify}`), `dry_run_supported`, `evidence_ref`.
- `MigrationEngine`: detect current version → target; run plan steps in order;
  each step reversible (has `down`); dry-run without mutation; verify gate
  before apply (fail-closed).
- State migration of durable state (`aios/goal_durability.DurableCheckpoint`)
  safely, with no data loss — sample state migration step provided.
- Integration with `aios/upgrade` (peer), `aios/goal_durability` (durable),
  `aios/harness.verification` (T032). No `agents/` imports.

**Out of scope**
- New runtime upgrade feature; new scheduler; new checkpoint service.
- Creating the `aios/durable` package (not present in this workspace; the
  durable state lives in `aios/goal_durability`, which is integrated instead).

## Deliverables
- `aios/upgrade/migration_plan.py` — `MigrationPlan`, `MigrationStep`,
  `MigrationEngine`, `MigrationReport`, `StepEvidence`, `MigrationError`,
  `MigrationPhase`, `hash_state`, `sample_durable_migration_step`,
  `make_durable_migration_plan`.
- `aios/upgrade/__init__.py` — exports the new symbols (engine as
  `MigrationPlanEngine` to avoid clobbering the existing `MigrationEngine`).
- `aios/upgrade/tests/test_migration_plan.py` — full AC + Test Matrix coverage.
- Lifecycle artifacts (this folder).

## Acceptance Criteria
- AC1: Migration Engine detects version and runs plan steps in order.
- AC2: Verify FAIL → step NOT applied (fail-closed).
- AC3: Every step reversible (has `down`); rollback succeeds.
- AC4: Dry-run runs without mutating state.
- AC5: Every step writes provenance evidence.
- AC6: Same plan + state → same result (deterministic).
- AC7: Durable state migrated safely, no data loss (T066).
- AC8: Integrates with Upgrade + Durable + Harness.
- AC9: Prior-milestone regression PASS; no invariant violations.

## Dependencies
- TASK-073 (AIOS 1.0 Certification Suite) — upstream.
- T066-equivalent durable state (`aios/goal_durability`) — integrated.
- T032 verification harness (`aios/harness.verification`) — integrated.

## Governance references
- Rule 3 (Architecture): `aios/upgrade` is an "unknown" layer; imports of
  `aios.goal_durability`, `aios.harness.verification`, `aios.upgrade.manifest`
  are permitted; `agents/` never imported.
- Rule 4/5/6/7 satisfied via deterministic engine, evidence provenance, and
  the test suite under `aios/upgrade/tests/`.
