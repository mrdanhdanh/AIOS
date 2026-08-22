# TASK-067 — Test

## How to run
```
python -m pytest aios/autonomy_safety -q
```

## What is covered
- **Unit** — `AutonomyContext`/`AutonomyLevelRegistry` assign/get, `raise_level` policy + human-approval gating.
- **Contract** — `SafeStopSignal` provenance; `SafetyDecision` enum values.
- **Boundary (Governor T054)** — in-boundary → ALLOW; out-of-boundary / over-budget → BLOCK; delegation proven against an independent Governor instance.
- **Safe-Stop** — boundary violation → SAFE_STOP fail-closed; kill-switch hook invoked; kill-switch raising still fail-closed.
- **Deterministic** — same context+action → identical decision + reason.
- **Escalation** — `escalate_on` risk class triggers ESCALATE; non-matching risk does not.
- **Integration** — Recovery `SAFE_STOP` strategy; Stuck `StuckSignal` → safe-stop.
- **Architecture** — no `agents/` import; only peer/unknown-layer packages imported.
