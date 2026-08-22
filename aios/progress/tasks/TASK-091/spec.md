# TASK-091 — Meta-Harness / Verify-the-Verifier

## Objective
Xây dựng **Meta-Harness (Verify-the-Verifier)** — kiểm tra chính harness: đảm bảo
harness (T030/T032/T078/T079/T089/T090) tự nó đúng, không sinh verdict sai, và có
thể bị verify. TASK-091 là **harness-of-harness, không phải feature mới**.

## Scope
**In scope:** `aios/meta_harness/` — MetaCheck, MetaResult, MetaHarness, MetaVerdict.
Tích hợp Harness (T030/T032) + Integrity (T078) + Coverage (T090).
**Out of scope:** harness mới; provider/filesystem adapters.

## Deliverables
- `aios/meta_harness/meta.py` — known-answer + mutation + verifier lock.
- `aios/meta_harness/tests/test_meta.py` — 7 tests (Test Matrix).
- Tích hợp với Harness (T030/T032) + Integrity (T078) + Coverage (T090).

## Acceptance Criteria
- Known-answer tests: harness trả verdict đúng với input mẫu.
- Mutation tests: harness phát hiện đột biến input.
- Harness sai verdict → meta FAIL (fail-closed).
- Verifier được khóa (T078).
- Mọi meta-run có provenance (T001 Rule 5).
- Cùng meta-input + harness → cùng meta-result (deterministic).
- Tích hợp được với Harness + Integrity + Coverage.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T090 (Harness Coverage) → T091 → T092.
- T030/T032 (Harness), T078 (Integrity), T090 (Coverage).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `meta_harness` là `unknown`
  layer; chỉ import stdlib + `aios.harness` + `aios.verification_integrity` + `aios.harness_coverage`.
