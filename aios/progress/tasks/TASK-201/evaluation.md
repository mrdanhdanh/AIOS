# TASK-201 — Evaluation

## Capability evaluation for Approval Gate
- Contract: immutable, I/O-free, capability-injected (`ApprovalGate`).
- Evidence: every transition/record carries content_hash provenance (T001 Rule 5).
- Determinism: same inputs -> same result id (sha256, no clock).
- Fail-closed: illegal state / missing artifact / out-of-range -> CodingEditionError.
- UNKNOWN is never promoted to PASS.

## Status
PASS — capability meets M26 acceptance criteria.
