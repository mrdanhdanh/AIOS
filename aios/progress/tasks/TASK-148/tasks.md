# TASK-148 — Task Breakdown

1. Định nghĩa `DiagnosticReport` (immutable `report_id`, `class_ref`, `observation_ref`, `root_cause`, `confidence`, `evidence_ref`).
2. `DiagnosticAgent.diagnose` fail-closed: yêu cầu failure class có provenance (T001 Rule 5).
3. UNKNOWN class → root_cause="UNKNOWN", confidence=0 (không promote, T078).
4. Deterministic root-cause mapping từ taxonomy.
5. `is_promotable` + `provenance()` (content_hash).
6. Tests (`test_diagnostic.py`): 7 tests.
7. Chạy pytest + gate_check + full suite.
