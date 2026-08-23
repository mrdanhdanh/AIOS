# TASK-151 — Verification Gate

## Objective
Triển khai **Verification Gate** (M21) như một năng lực có contract, evidence và harness riêng — xác minh output của loop (T150) trước khi promote PASS, fail-closed, dựa trên Verification Engine (T142) + Verification Integrity (T078). TASK-151 là **gate, không phải verifier mới** (dựa trên Progress/Regression Detection T150 + Verification Engine T142 + Integrity T078 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/verification_gate.py` — `VerificationGate`, `VerificationResult`, `VerifyStatus`.
**Out of scope:** verifier mới (T142).

## Deliverables
- `aios/coding_loop/verification_gate.py` implementation + gate.
- Policy Boundary (T113) trên mọi verification.
- Integration với Progress/Regression Detection (T150) + Verification Engine (T142) + Integrity (T078) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_verification_gate.py`).

## Acceptance Criteria
- Verification Gate xác minh output loop (T150).
- Verification FAIL/INCONCLUSIVE → không promote PASS (fail-closed, T078).
- Mọi verification có provenance (T001 Rule 5).
- Cùng output → cùng result (deterministic).
- Verification không lộ secret (T040/T113).
- Tích hợp được với Progress/Regression Detection + Verification Engine + Integrity + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T150 (Progress + Regression Detection), T142 (Verification Engine), T078 (Integrity).
- T001 (Rule 5), T078 (Integrity), T040/T113 (Security).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
