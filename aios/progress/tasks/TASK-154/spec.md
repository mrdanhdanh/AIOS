# TASK-154 — Autonomous Coding Harness

## Objective
Triển khai **Autonomous Coding Harness** (M21) như một năng lực có contract, evidence và harness riêng — harness tích hợp toàn bộ coding loop (T145→T153) trên nền Harness Kernel (T029) + Test Harness (T031) + Evaluation Harness (T032). TASK-154 là **harness tích hợp, không phải loop mới** (dựa trên toàn bộ M21 T145→T153 + Harness Kernel T029 + Test Harness T031 + Evaluation Harness T032 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/harness.py` — `AutonomousCodingHarness`, `CodingHarnessRun`, `HarnessStatus`.
**Out of scope:** loop mới (T145→T153).

## Deliverables
- `aios/coding_loop/harness.py` implementation + orchestration.
- Policy Boundary (T113) trên mọi run.
- Integration với toàn bộ M21 (T145→T153) + Harness Kernel (T029) + Test Harness (T031) + Evaluation Harness (T032) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_harness.py`).

## Acceptance Criteria
- Harness điều phối toàn bộ loop T145→T153 end-to-end.
- Harness chạy scenario từ Test Harness (T031).
- Harness đo metric từ Evaluation Harness (T032).
- Mọi run có provenance (T001 Rule 5).
- Cùng input → cùng output (deterministic, T029/T079).
- Tích hợp được với toàn bộ M21 + Harness Kernel + Test Harness + Evaluation Harness + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T145→T153 (toàn bộ M21), T029 (Harness Kernel), T031 (Test Harness + Scenario), T032 (Evaluation Harness).
- T001 (Rule 5), T078 (Integrity), T029/T079 (Deterministic), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
