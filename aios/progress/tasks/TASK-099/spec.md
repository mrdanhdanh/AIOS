# TASK-099 — Autonomous Harness Loop

## Objective
Xây dựng **Autonomous Harness Loop** — vòng lặp tự chủ chạy harness (T030/T032/T078/T079/T089/T091) lên chính hệ thống, phát hiện deviation và kích hoạt remediation (T094-T098) một cách autonomy-aware và fail-closed. TASK-099 là **self-testing loop, không phải harness mới**.

## Scope
**In scope:** `aios/autonomous_harness_loop/` — HarnessLoopRun, HarnessLoopEngine. Tích hợp Scheduler (T062) + Harness chain + Detect (T094) + Remediation (T095-T098) + Governor (T054/T067).
**Out of scope:** xây harness mới; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/autonomous_harness_loop/loop.py` — loop engine (6 tests).
- `aios/autonomous_harness_loop/tests/test_loop.py` — 6 tests (Test Matrix).
- Tích hợp Scheduler (T062) + Harness chain + Detect (T094) + Remediation (T095-T098) + Governor (T054/T067).

## Acceptance Criteria
- Harness chạy định kỳ/trigger (T062).
- Toàn bộ harness chain được thực thi.
- Deviation → không auto-promote PASS (fail-closed).
- Remediation chỉ trigger khi autonomy allow (T054/T067).
- Mọi vòng lặp có provenance (T001 Rule 5).
- Cùng system state + harness → cùng loop result (deterministic).
- Tích hợp được với Autonomous Loop + Harness chain + Remediation + Scheduler.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T098 (Remediation Integrity + Kill Switch) → T099 → T100.
- T062 (Scheduler), T030/T032 (Harness), T078/T091 (Integrity/Meta), T094-T098 (Remediation), T054/T067 (Governor).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `autonomous_harness_loop` là `unknown` layer; chỉ import stdlib + `aios.autonomous_scheduler` + `aios.harness.verification` + `aios.verification_integrity` + `aios.meta_harness` + `aios.remediation_*` + `aios.autonomy_governor` + `aios.governance.evidence`.
