# Task Breakdown — TASK-086

- [x] CompatSurface enum (API/SCHEMA/EVENT).
- [x] CompatCheck dataclass (surface, consumer_version, provider_version, breaking, evidence_ref).
- [x] CompatResult dataclass (compatible, blocked, reason).
- [x] BackwardCompatChecker.check (breaking → BLOCK fail-closed).
- [x] BackwardCompatChecker.run_suite (fail-closed).
- [x] CompatTestSuite (locks 1.0 behavior).
- [x] BackwardCompatChecker.provenance_complete / suite_hash.
- [x] Tests 7 cases (Test Matrix).
- [x] Tích hợp Contract (T064) + Version (T084) + Migration (T085).
