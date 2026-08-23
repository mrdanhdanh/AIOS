# TASK-128 — Patch Engine

## Objective
Triển khai **Patch Engine** (M19) như một năng lực có contract, evidence và harness riêng — áp dụng code artifact (T127) thành patch an toàn (diff/apply/rollback) lên repository, không phá Core. TASK-128 là **patch engine, không phải generator mới** (dựa trên Code Generation T127 + Upgrade/Migration T020 + Durable T066).

## Scope
**In scope:** `aios/coder/patch.py` — `PatchEngine`, `PatchRun`, `PatchStatus`, `PatchError`.
**Out of scope:** review agent (T129); coding artifact/evidence (T130).

## Deliverables
- `aios/coder/patch.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_patch.py`.
- Tích hợp: T127 -> T128 -> T129/T130 (M19).

## Acceptance Criteria
- Patch Engine tạo diff từ artifact (T127) và apply an toàn.
- Apply có backup trước (T020); fail → rollback (T020/T066).
- Mọi patch có `content_hash` (T078) + provenance (T001 Rule 5).
- Apply fail → rollback, không để repo hỏng (fail-closed).
- Cùng artifact + target → cùng diff (deterministic).
- Tích hợp được với Generation + Upgrade + Durable + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T127 (Generation) -> T128 -> T129/T130.
- T001 (Rule 5), T020 (Upgrade/Migration), T066 (Durable), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
