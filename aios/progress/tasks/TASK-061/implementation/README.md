# TASK-061 Implementation

## Modules
- `contracts.py` — `StuckSignal`, `StuckKind`, `StuckSeverity`, `StuckPolicy` (policy-driven, fail-closed).
- `detector.py` — `StuckDetector` (monitors every iteration; oscillation via trajectory hash, plateau, resource-burn), `StuckGate` (Governor authorize + autonomy budget).

## Design notes
- Detect ≠ Decide ≠ Recover: detector emits signal, StuckPolicy maps to candidate, Governor/Recovery decide permission.
- Fail-closed: low confidence or missing evidence → escalate, never auto-continue.
- Deterministic: same trajectory + detector config → same verdict.
