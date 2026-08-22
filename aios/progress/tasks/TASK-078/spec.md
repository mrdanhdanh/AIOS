# TASK-078 — Verification Integrity / Fail-Closed Gate

## Objective
Hoàn thiện **Verification Integrity** — đảm bảo mọi verification (T030) và evaluation
(T032) có tính toàn vẹn (integrity) và luôn vận hành **fail-closed**: verdict không xác
định / không thể verify → KHÔNG promote thành PASS. TASK-078 là integrity + fail-closed
gate, không phải verification engine mới (dựa trên Harness T030/T032 + Evidence T001).

## Scope
**In scope:** `aios/verification_integrity/` — IntegrityReport, VerifierLock,
IntegrityChecker (hash/signature, verifier lock, fail-closed verdict, tamper detection,
provenance lock). Tích hợp Harness + Evidence + Evaluation.
**Out of scope:** thay thế harness; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/verification_integrity/integrity.py` — IntegrityReport, VerifierLock, IntegrityChecker.
- `aios/verification_integrity/tests/test_integrity.py` — 8 tests (Test Matrix).
- Tích hợp với Harness (T030/T032) + Evidence (T001).

## Acceptance Criteria
- Mọi evidence/verdict có content_hash; thay đổi → reject (fail-closed).
- Verifier version + config khóa per run.
- UNKNOWN/INCONCLUSIVE → KHÔNG promote thành PASS.
- Evidence bị sửa → reject (tamper detection).
- Cùng evidence + verifier → cùng verdict (deterministic).
- Provenance chain complete (T001 Rule 5).
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T077 (reserved) → T078 → T079.
- T001 (Rule 5 evidence), T030 (verification), T032 (evaluation).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `verification_integrity` là `unknown`
  layer; chỉ import stdlib + `aios.governance.evidence` + `aios.harness`.
