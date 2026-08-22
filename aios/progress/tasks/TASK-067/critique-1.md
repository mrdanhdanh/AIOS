# TASK-067 — Critique 1

## Strengths
- Clear separation: safety layer delegates all authority to Governor (T054); no parallel controller (satisfies AC7).
- Fail-closed SAFE_STOP is the correct default for boundary violations.
- Reuses existing contracts from T054/T055/T061 instead of inventing new ones.

## Risks / Gaps
- Kill Switch (T068) is not yet available — must define a `SafeStopSignal` type and a hook, not assume T068 exists.
- "Boundary" must be concretely defined: map `allowed_surfaces` → Governor `capabilities` scope so out-of-surface actions are BLOCKed.
- Escalation (`escalate_on`) must be evaluated only after the Governor ALLOWs, otherwise every risky blocked action would also "escalate".

## Required revisions
- Define `SafeStopSignal` in `contracts.py` with `evidence_ref` provenance.
- Make `check_boundary` map Governor BLOCK/ASK → safety BLOCK (fail-closed for autonomous execution).
- Order `evaluate_action`: boundary → SAFE_STOP; then escalation; then ALLOW.
