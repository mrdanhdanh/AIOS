# Breakdown — TASK-131

1. `aios/coder/conformance.py` — `CoderConformanceHarness` (validate invariants M19).
2. Invariants: content_hash khớp, evidence_present (T001), integrity_verified (T078), producer authorized, no forbidden ops.
3. `ConformanceResult` (status, security, reasons, content_hash, evidence_id).
4. Fail-closed: thiếu invariant / security DENIED → FAIL; `promote()` từ chối UNKNOWN (T078).
5. Tests (9) theo Test Matrix TASK-131 + architecture guard.
6. Tích hợp: T125→T130 -> T131 (M19).
