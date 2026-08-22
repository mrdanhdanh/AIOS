# TASK-105 — Independent Verification Oracle

## Objective
Xây **Independent Verification Oracle** — map các invariant checkable sang independent harness oracle, và **bridge evidence từ independent harness vào AIOS verification**; **không chuyển authority khỏi AIOS policy**. Oracle bridge, không phải verification engine mới (dựa trên Foundation T104 + Harness T030/T032 + Integrity T078 + Evidence T001).

## Scope
**In scope:** `aios/independent_harness/oracle.py` — `OracleResult`, `InvariantMapping`, `IndependentVerificationOracle` + tests. Tích hợp Foundation (T104) + Harness + Integrity + Evidence.
**Out of scope:** verification engine mới; provider/filesystem adapters.

## Deliverables
- `aios/independent_harness/oracle.py` — oracle adapter/mapping/bridge/authority (6 tests).
- Tests Test Matrix T105.
- Tích hợp Foundation (T104) + Harness (T030/T032) + Integrity (T078) + Evidence (T001).

## Acceptance Criteria
- Oracle Adapter map được invariant sang independent harness check.
- Evidence từ oracle được bridge vào AIOS verification (qua T104).
- **AIOS giữ authority/policy boundary** — oracle conflict không override AIOS.
- Verdict oracle không xác định → INCONCLUSIVE → không promote PASS (T078).
- Mọi bridge có provenance (T001 Rule 5).
- Cùng invariant + oracle input → cùng `independent_verdict` (deterministic).
- Tích hợp được với Foundation + Harness + Integrity + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T104 → T105 → T106/T107.
- T030/T032 (Harness), T078 (Integrity), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. `independent_harness` là `unknown` layer.
