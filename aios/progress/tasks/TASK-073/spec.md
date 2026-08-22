# TASK-073 — AIOS 1.0 Certification Suite

## Objective
Xây dựng Certification Suite 1.0: bộ test/chứng nhận một build AIOS 1.0 thỏa mãn
mọi invariant, contract và governance gate trước khi release. Đây là certification
harness, không phải feature mới (dựa trên `aios/certification`, governance gates T001).

## Scope
- Certifier chạy toàn bộ gate + conformance, sinh release certificate.
- Release gate fail-closed (một gate FAIL → không cấp certificate).
- Certificate có provenance (evidence chain).

## Deliverables
- `aios/certification/release.py` — `ReleaseCertifier`, `ReleaseCertificate`, `GateResult`, default gate builders (architecture T063, contract T064, harness T032/T030, governance T001).
- Tests `aios/certification/tests/test_release.py`.

## Acceptance Criteria
- AC1: Mọi governance gate (T001) chạy trong cert suite.
- AC2: Architecture guard (T063) + contract conformance (T064) chạy.
- AC3: Một gate FAIL → không cấp certificate (fail-closed).
- AC4: Certificate có provenance đầy đủ.
- AC5: Cùng build + suite → cùng kết quả cert (deterministic).
- AC6: Tích hợp được với Certification + Governance + Harness.
- AC7: Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- TASK-063 Architecture 1.0, TASK-064 Public Contract Freeze, TASK-072 Dashboard 1.0.

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`. No parallel certifier.
