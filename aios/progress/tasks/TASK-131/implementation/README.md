# TASK-131 Implementation

Coder Conformance Harness + Security lives in:

- `aios/coder/conformance.py` — `CoderConformanceHarness`, `ConformanceResult`, `ConformanceStatus`, `SecurityStatus`, `ConformanceError`.
- Tests trong `aios/coder/tests/test_conformance.py` (9 tests, Test Matrix TASK-131).

Design:
- `CoderConformanceHarness.check()` validate invariants M19: content_hash khớp, evidence_present (T001 Rule 5), integrity_verified (T078), producer authorized, no forbidden ops (subprocess/os.system/rm -rf). Thiếu → FAIL; security DENIED → FAIL.
- `promote()` fail-closed: UNKNOWN/FAIL không bao giờ → PASS (T078).
- Mọi `ConformanceResult` ghi `evidence_id` + `content_hash` (sha256) — provenance (T001 Rule 5).

Integration (import-level, no rewrite):
- `aios.coder.artifact` (T130) / `aios.coder.generation` (T127) / `aios.coder.review` (T129) — validated artifacts
- `aios.governance.evidence` (T001) / `aios.verification_integrity` (T078) / `aios.security` (T113)
- `aios.coder.conformance` (T131) -> `aios.coder.autonomy` (T132)
