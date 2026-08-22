# TASK-098 — Remediation Integrity + Kill Switch

## Objective
Đảm bảo **Remediation Integrity** — toàn bộ chuỗi remediation (T094-T097) có tính
toàn vẹn (integrity) và có thể kích hoạt **Kill Switch** (T068) để dừng remediation
đang chạy nếu phát hiện nguy hiểm. TASK-098 là **integrity + emergency stop cho
remediation, không phải remediation mới** (dựa trên Integrity T078 + Kill Switch T068
+ Remediation T094-T097).

## Scope
**In scope:** `aios/remediation_integrity/` — RemediationArtifact, RemediationIntegrity,
RemediationIntegrityGate. Tích hợp Integrity (T078) + Kill Switch (T068) + Remediation (T094-T097).
**Out of scope:** remediation mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/remediation_integrity/integrity.py` — integrity check + kill switch hook.
- `aios/remediation_integrity/tests/test_integrity.py` — 6 tests (Test Matrix).
- Tích hợp với Integrity (T078) + Kill Switch (T068) + Remediation (T094-T097).

## Acceptance Criteria
- Mọi artifact remediation có hash/signature (T078).
- Artifact bị sửa → reject (fail-closed).
- Mọi bước remediation ghi audit trail.
- Remediation đang chạy tôn trọng Kill Switch (T068).
- Mọi integrity check có provenance (T001 Rule 5).
- Cùng artifact + check → cùng result (deterministic).
- Tích hợp được với Integrity + Kill Switch + Remediation.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T097 (Apply + Rollback) → T098 → T099 (M15).
- T078 (Integrity), T068 (Kill Switch), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `remediation_integrity` là `unknown`
  layer; chỉ import stdlib + `aios.verification_integrity` + `aios.kill_switch` + `aios.governance.evidence`.
