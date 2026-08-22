# TASK-103 — Autonomy Constitution + Audit Trail

## Objective
Soạn **Autonomy Constitution** — văn bản quy định tối cao về giới hạn tự chủ, và **Audit Trail** — chuỗi ghi nhận bất biến mọi quyết định tự chủ để truy tra và chịu trách nhiệm. TASK-103 là **constitution + audit, không phải runtime feature** (dựa trên T067 + T102 + T001 + T068 + T078).

## Scope
**In scope:** `aios/autonomy_constitution/` — AuditEntry, AutonomyConstitution, AuditTrail, ConstitutionEngine + CONSTITUTION.md (ADR). Tích hợp Autonomy Safety (T067) + Trust Budget (T102) + Evidence (T001) + Integrity (T078) + Kill Switch (T068).
**Out of scope:** runtime autonomy execution mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/autonomy_constitution/constitution.py` — constitution + audit engine (6 tests).
- `aios/autonomy_constitution/CONSTITUTION.md` — ADR (supreme rules).
- `aios/autonomy_constitution/tests/test_constitution.py` — 6 tests (Test Matrix).
- Tích hợp Autonomy Safety (T067) + Trust Budget (T102) + Evidence (T001) + Integrity (T078) + Kill Switch (T068).

## Acceptance Criteria
- Autonomy Constitution định nghĩa giới hạn tối cao (supreme law).
- Quyết định vi phạm constitution → BLOCK (fail-closed).
- Audit Trail bất biến (immutable chain, tamper-evident T078).
- Mọi decision trace được về principal + policy (accountability).
- Mọi entry có provenance (T001 Rule 5).
- Cùng decision + constitution → cùng compliance result (deterministic).
- Tích hợp được với Autonomy + Trust + Evidence + Integrity + Kill Switch.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T102 (Trust Budget) → T103 → T104 (M16).
- T067 (Autonomy Safety), T102 (Trust), T001 (Evidence), T078 (Integrity), T068 (Kill Switch).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `autonomy_constitution` là `unknown` layer; chỉ import stdlib + `aios.autonomy_safety` + `aios.autonomy_governor` + `aios.trust_budget` + `aios.kill_switch` + `aios.verification_integrity` + `aios.governance.evidence`.
