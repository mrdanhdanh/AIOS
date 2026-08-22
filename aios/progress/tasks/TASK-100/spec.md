# TASK-100 — Failure-Corpus Improvement Engine

## Objective
Xây dựng **Failure-Corpus Improvement Engine** — thu thập failure/deviation thực tế (từ T094/T099), duy trì corpus versioned + deduplicated, chạy gap analysis (T090) và đề xuất cải thiện harness/detection/remediation. TASK-100 là **corpus-driven improvement, không phải harness mới**.

## Scope
**In scope:** `aios/failure_corpus/` — CorpusEntry, FailureCorpus, FailureCorpusEngine. Tích hợp Detect (T094) + Loop (T099) + Coverage (T090) + Evidence (T001).
**Out of scope:** xây harness mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/failure_corpus/corpus.py` — corpus engine (6 tests).
- `aios/failure_corpus/tests/test_corpus.py` — 6 tests (Test Matrix).
- Tích hợp Detect (T094) + Loop (T099) + Coverage (T090) + Evidence (T001).

## Acceptance Criteria
- Failure thu thập từ T094/T099.
- Corpus store versioned + deduplicated + content_hash.
- Gap (chưa covered) được report (không giấu, T090).
- Improvement đề xuất cho harness/detection/remediation.
- Mọi entry có provenance (T001 Rule 5).
- Cùng failure + corpus → cùng analysis (deterministic).
- Tích hợp được với Detect + Loop + Coverage + Harness chain.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T099 (Autonomous Harness Loop) → T100 → T101.
- T094 (Detect), T090 (Coverage), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `failure_corpus` là `unknown` layer; chỉ import stdlib + `aios.remediation_detect` + `aios.autonomous_harness_loop` + `aios.harness_coverage` + `aios.verification_integrity` + `aios.governance.evidence`.
