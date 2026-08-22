# TASK-075 — Critique 1

## Strengths
- Builds on the existing, well-tested `aios/model_router` (T025) rather than a rewrite.
- Reuses `aios.governance.deterministic.DeterministicControlPath` (Rule 4) and
  `aios.autonomous_recovery` (T055) — no duplicated control logic.
- Fail-closed everywhere: no eligible model, budget exceeded, unknown failure.

## Risks / Gaps
- `aios/reliability` (T069) and `aios/autonomy_safety` / `aios/kill_switch` are absent in
  the codebase; SLO + escalate/stop are implemented locally with clear integration notes.
- `route()` accepts `**requirement_kwargs` — must not be used to smuggle a hardcoded
  `preferred_provider` that defeats policy-driven selection (kept as a capability, not a
  default).

## Required revisions
- Confirm `ModelRoute` carries `evidence_ref` + `provenance` for AC6.
- Confirm `attempt_fallback` defers the strategy decision to `RecoveryController` (T055)
  rather than hardcoding fallback.
- Add explicit tests for the "unknown failure → SAFE_STOP → no route" fail-closed path.
