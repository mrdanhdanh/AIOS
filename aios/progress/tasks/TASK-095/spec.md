# TASK-095 — Candidate Generation + Risk Scoring

## Objective
Sau khi detect + diagnose (T094), sinh các phương án khắc phục (candidates) và
chấm điểm rủi ro (risk scoring) cho từng phương án, để chọn candidate an toàn
nhất đưa vào remediation. TASK-095 là **candidate + risk, không phải apply**
(dựa trên Diagnosis T094 + Policy T054).

## Scope
**In scope:** `aios/remediation_candidate/` — Candidate, CandidateGenerator,
RiskScorer, PolicyFilter, CandidateRanker, CandidateEngine. Tích hợp Diagnosis (T094)
+ Governor/Policy (T054/T067).
**Out of scope:** apply/rollback; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/remediation_candidate/candidate.py` — generate + score + filter + rank.
- `aios/remediation_candidate/tests/test_candidate.py` — 7 tests (Test Matrix).
- Tích hợp với Diagnosis (T094) + Governor/Policy (T054) + Autonomy (T067).

## Acceptance Criteria
- Candidate được sinh từ diagnosis (T094).
- Risk scoring chấm điểm mỗi candidate.
- Candidate vi phạm policy → loại (fail-closed).
- Risk score evidence-based.
- Mọi candidate có provenance (T001 Rule 5).
- Cùng diagnosis + policy → cùng ranking (deterministic).
- Tích hợp được với Diagnosis + Governor/Policy + Autonomy.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T094 (Detect + Diagnose) → T095 → T096.
- T054 (Governor), T067 (Autonomy), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `remediation_candidate` là `unknown`
  layer; chỉ import stdlib + `aios.autonomy_governor` + `aios.remediation_detect` + `aios.governance.evidence`.
