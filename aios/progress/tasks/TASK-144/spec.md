# TASK-144 — Execution Evidence + Conformance

## Objective
Triển khai **Execution Evidence + Conformance** (M20) như một năng lực có contract, evidence và harness riêng — chuẩn hóa execution evidence xuyên suốt pipeline T135→T143 và chạy conformance fail-closed. TASK-144 là **evidence + conformance chuẩn, không phải pipeline mới** (dựa trên Execution Contract T135 + Sandbox T136 + Workspace T137 + Policy T138 + Test T139 + Build/Lint T140 + Collector T141 + Verification T142 + Security/Replay T143 + Evidence T001 Rule 5 + Integrity T078).

## Scope
**In scope:** `aios/execution/evidence.py` — `ExecutionEvidenceRegistry`, `ExecutionEvidence`, `EvidenceStatus`.
**Out of scope:** pipeline mới (T135–T143).

## Deliverables
- `aios/execution/evidence.py` implementation + conformance gate.
- Unit + Contract + Integration + Architecture + Regression tests (`test_evidence.py`).
- Tích hợp: T135→T143 -> T144 (đóng M20).

## Acceptance Criteria
- Execution Evidence chuẩn hóa có `content_hash` (T078).
- Mọi evidence có provenance chain đầy đủ (T001 Rule 5).
- Evidence không verify -> không promote PASS (fail-closed, T078).
- `evidence_id` immutable (T001 Rule 1).
- Cùng evidence + verifier -> cùng verdict (deterministic).
- Tích hợp được với pipeline T135→T143 + Evidence + Integrity + Policy.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T135..T143 -> T144 (đóng M20).
- T001 (Rule 1/5), T078 (Integrity), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
