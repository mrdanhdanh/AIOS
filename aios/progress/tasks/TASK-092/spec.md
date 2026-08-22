# TASK-092 — System Readiness vs Harness Trust

## Objective
Thiết lập mối quan hệ **System Readiness vs Harness Trust** — chỉ khi harness đủ
trust (T090/T091) thì system mới được coi là ready để chứng nhận; ngược lại system
sẵn sàng nhưng harness chưa trust → không certify. TASK-092 là **readiness/trust
gate, không phải feature mới** (dựa trên Coverage T090 + Meta T091 + Certification T073).

## Scope
**In scope:** `aios/readiness_trust/` — ReadinessTrust, CombinedTrust, TrustGate.
Tích hợp Coverage (T090) + Meta (T091) + Certification (T073).
**Out of scope:** system feature mới; provider/filesystem adapters.

## Deliverables
- `aios/readiness_trust/trust.py` — combined gate (ready AND trusted → certify).
- `aios/readiness_trust/tests/test_trust.py` — 6 tests (Test Matrix).
- Tích hợp với Coverage (T090) + Meta (T091) + Certification (T073).

## Acceptance Criteria
- System Readiness được đo (health + gates).
- Harness Trust được đo (T090/T091).
- System ready nhưng harness untrusted → KHÔNG certify (fail-closed).
- Chỉ READY_TRUSTED mới certify.
- Mọi trust decision có provenance (T001 Rule 5).
- Cùng system + harness → cùng trust result (deterministic).
- Tích hợp được với Coverage + Meta + Certification.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T091 (Meta-Harness) → T092 → T093.
- T090 (Coverage), T091 (Meta), T073 (Certification).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `readiness_trust` là `unknown`
  layer; chỉ import stdlib + `aios.harness_coverage` + `aios.meta_harness` + `aios.certification`.
