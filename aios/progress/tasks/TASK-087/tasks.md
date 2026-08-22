# Task Breakdown — TASK-087

- [x] ConformanceCheck enum (api/schema/event/version/contract).
- [x] ConformanceReport dataclass (target_version, baseline, checks_passed, issued_at, evidence_ref, conformant).
- [x] ConformanceRunner._check_surface / _check_version / _check_contract.
- [x] ConformanceRunner.run (5 checks, fail-closed).
- [x] ConformanceRunner.issue (gate).
- [x] ConformanceRunner.certify (T073 integration, fail-closed).
- [x] ConformanceRunner.report_hash / provenance_complete.
- [x] Tests 7 cases (Test Matrix).
- [x] Tích hợp Certification (T073) + Contract (T064) + Version (T084) + Backward (T086).
