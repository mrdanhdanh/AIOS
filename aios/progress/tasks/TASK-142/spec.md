# TASK-142 — Verification Engine

## Objective
Triển khai **Verification Engine** (M20) như một năng lực có contract, evidence và harness riêng — xác minh collected artifact/output (T141) theo contract, fail-closed, không promote PASS khi không verify được. TASK-142 là **verification engine, không phải collector mới** (dựa trên Collector T141 + Verification Integrity T078 + Evidence T001).

## Scope
**In scope:** `aios/execution/verification.py` — `VerificationEngine`, `VerificationResult`, `VerifyStatus`.
**Out of scope:** collector mới (T141), security/replay (T143).

## Deliverables
- `aios/execution/verification.py` implementation + integrity gate.
- Unit + Contract + Integration + Architecture + Regression tests (`test_verification.py`).
- Tích hợp: T141 -> T142 -> T143.

## Acceptance Criteria
- Verification Engine xác minh collected artifact/output (T141).
- Verification FAIL/INCONCLUSIVE -> không promote PASS (fail-closed, T078).
- Mọi verification có provenance (T001 Rule 5).
- Cùng artifact -> cùng result (deterministic).
- Verification không lộ secret (T040/T113).
- Tích hợp được với Collector + Integrity + Evidence + Security/Replay.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T141 (Collector) -> T142 -> T143.
- T001 (Rule 5), T078 (Integrity), T040/T113 (Secret).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
