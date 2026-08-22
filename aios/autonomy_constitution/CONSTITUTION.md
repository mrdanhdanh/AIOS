# Autonomy Constitution (Supreme Law)

> Canonical document for TASK-103 (M15). This is the **supreme autonomy law** of
> AIOS: every autonomous action MUST comply. A violation is fail-closed BLOCKed.

## Articles

- **A1 — Human oversight for destructive action.** Any `destructive` autonomy
  action requires an explicit human approval recorded in `policy_ref`
  (e.g. `approval:req-123`). Absent approval → BLOCK.
- **A2 — Halt supremacy.** While a Kill Switch (T068) halt is active, no autonomy
  action may proceed. `halt_active` → BLOCK.
- **A3 — Trust budget bound.** An action must stay within its Trust Budget
  (T102): `trust_remaining > 0`. An empty budget → BLOCK (SAFE-STOP).
- **A4 — Critical risk escalation.** A `critical` risk action requires a policy
  escalation recorded in `policy_ref` (e.g. `escalation:pol-9`). Absent
  escalation → BLOCK.

## Properties

- **Fail-closed:** any article violation → `constitution_compliant = False` → BLOCK.
- **Immutable audit:** every decision is appended to a hash-chained `AuditTrail`;
  entries are never edited or deleted.
- **Tamper-evident:** editing any entry is detected via `IntegrityChecker` (T078)
  because the next entry's `prev_entry_hash` no longer matches.
- **Accountability:** each `AuditEntry` records `principal` + `policy_ref` so any
  decision is traceable.
- **Provenance:** every entry carries an `evidence_ref` (T001 Rule 5).
- **Deterministic:** same decision + same constitution → same compliance result.
