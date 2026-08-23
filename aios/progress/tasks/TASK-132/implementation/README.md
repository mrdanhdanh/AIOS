# TASK-132 Implementation

Autonomy Level + Permission Integration lives in:

- `aios/coder/autonomy.py` — `AutonomyLevel`, `AutonomyPermissionBroker`, `PermissionDecision`, `PermissionError_`.
- Tests trong `aios/coder/tests/test_autonomy.py` (9 tests, Test Matrix TASK-132).

Design:
- 3 autonomy levels: SUPERVISED {plan,review}, ASSISTED {+generate}, AUTONOMOUS {+apply,patch}.
- `AutonomyPermissionBroker.check()` fail-closed (T113): op không thuộc level set / policy reject / unknown op → allowed=False (never silent-allow). `require()` raise `PermissionError_` khi denied.
- Mọi `PermissionDecision` ghi `evidence_id` + `content_hash` (sha256) — provenance (T001 Rule 5).

Integration (import-level, no rewrite):
- `aios.coder.contract` (T125) — agent boundary
- `aios.security` (T113) — permission broker semantics
- `aios.coder.autonomy` (T132) -> `aios.coder.prompt` (T133) / `aios.coder.filesafety` (T134)
