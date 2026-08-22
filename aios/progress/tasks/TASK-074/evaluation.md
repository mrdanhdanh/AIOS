# TASK-074 — Evaluation

## Acceptance criteria results
| AC | Description | Result | Evidence (test) |
|----|-------------|--------|-----------------|
| AC1 | Engine detects version + runs plan in order | PASS | `TestVersionDetection`, `TestOrderedExecution` |
| AC2 | Verify FAIL → not applied (fail-closed) | PASS | `TestVerifyFailClosed::test_verify_fail_not_applied` |
| AC3 | Every step reversible (`down`); rollback succeeds | PASS | `TestRollback`, `TestSafetyProperties::test_irreversible_plan_rejected` |
| AC4 | Dry-run runs without mutating state | PASS | `TestDryRun::test_dry_run_no_mutate` |
| AC5 | Every step writes provenance evidence | PASS | `TestSafetyProperties::test_every_step_writes_evidence` |
| AC6 | Same plan + state → same result (deterministic) | PASS | `TestDeterministic` |
| AC7 | Durable state migrated safely, no data loss (T066) | PASS | `TestDurableStateMigration` |
| AC8 | Integrates with Upgrade + Durable + Harness | PASS | `TestPeerIntegration`, `TestDurableStateMigration` |
| AC9 | Prior-milestone regression PASS; no invariant violations | PASS | `python -m pytest aios/upgrade -q` → 64 passed |

## Test Matrix
| Scenario | Expected | Result |
|----------|----------|--------|
| version detect | plan đúng | PASS |
| verify FAIL | không apply (fail-closed) | PASS |
| bước có down | rollback thành công | PASS |
| dry-run | không mutate | PASS |
| migrate state | không mất data (T066) | PASS |
| cùng plan + state | cùng kết quả (deterministic) | PASS |

## Notes
- `aios/durable` (T066) named in the request is **not present** in this
  workspace; the durable state is `aios/goal_durability`, which is integrated
  instead (avoids a broken import and satisfies the "no data loss" AC).
- `aios/execution_verification` (T032) is the `aios/harness/verification`
  module, integrated via `VerificationPipeline`/`Verdict`.
