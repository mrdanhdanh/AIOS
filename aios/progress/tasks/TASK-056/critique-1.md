# TASK-056 — Critique 1

## Missing spec sections
- Checkpoint field set enumerated in `contracts.DurableCheckpoint` with `content_hash` via `compute_hash`.
- Resume verdicts (VALID/INVALID/STALE/INCONCLUSIVE) in `ResumeVerdict`.

## Risks
- Old checkpoint overwriting new. Mitigation: coordinator auto-assigns monotonic `sequence = current+1`; store keeps only latest.
- Resume from invalid state. Mitigation: `validate` checks hash + evidence + policy; fail-closed returns INVALID/INCONCLUSIVE.
- Duplicate side effects. Mitigation: `acknowledge_action` / `is_action_acknowledged` idempotency keys.

## Verdict
Implementable. Proceed.
