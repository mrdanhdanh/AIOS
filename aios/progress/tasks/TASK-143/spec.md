# TASK-143 — Security + Replay Harness

## Objective
Triển khai **Security + Replay Harness** (M20) như một năng lực có contract, evidence và harness riêng — chạy execution (T135) trong sandbox (T136) dưới policy (T138) và cho phép replay deterministic từ evidence (T141/T142). TASK-143 là **security + replay harness, không phải runner mới** (dựa trên Execution T135 + Sandbox T136 + Policy T138 + Collector T141 + Verification T142 + Replay T030 + Integrity T078).

## Scope
**In scope:** `aios/execution/replay.py` — `SecurityReplayHarness`, `ReplayRun`.
**Out of scope:** runner mới (T139/T140), evidence/conformance (T144).

## Deliverables
- `aios/execution/replay.py` implementation + determinism check.
- Unit + Contract + Integration + Architecture + Regression tests (`test_replay.py`).
- Tích hợp: T135/T136/T138/T141/T142 -> T143 -> T144.

## Acceptance Criteria
- Harness chạy execution trong sandbox (T136) dưới policy (T138).
- Replay từ evidence (T141/T142) deterministic (T030).
- Replay không khớp -> phát hiện (fail-closed, T078).
- Mọi replay có provenance (T001 Rule 5).
- Cùng evidence -> cùng output (deterministic).
- Tích hợp được với Execution + Sandbox + Policy + Collector + Verification + Replay + Integrity.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T135 + T136 + T138 + T141 + T142 -> T143 -> T144.
- T001 (Rule 5), T030 (Replay), T078 (Integrity), T040 (Sandbox).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
