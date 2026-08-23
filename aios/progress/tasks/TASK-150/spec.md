# TASK-150 — Progress + Regression Detection

## Objective
Triển khai **Progress + Regression Detection** (M21) như một năng lực có contract, evidence và harness riêng — phát hiện tiến độ và regression của loop (T149) dựa trên Benchmark/Regression (T033) + Autonomous Recovery (T055). TASK-150 là **detector, không phải verifier mới** (dựa trên Repair Planner T149 + Benchmark/Regression T033 + Autonomous Recovery T055 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/progress_detection.py` — `ProgressRegressionDetector`, `ProgressReport`.
**Out of scope:** verifier mới (T151).

## Deliverables
- `aios/coding_loop/progress_detection.py` implementation + detector.
- Policy Boundary (T113) trên mọi detection.
- Integration với Repair Planner (T149) + Benchmark/Regression (T033) + Autonomous Recovery (T055) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_progress_detection.py`).

## Acceptance Criteria
- Detection đo được tiến độ loop (T145→T149).
- Regression phát hiện được so với baseline (T033).
- Mọi report có provenance (T001 Rule 5).
- Cùng state → cùng verdict (deterministic).
- Regression → loop quay lại repair/stop (T055).
- Tích hợp được với Repair Planner + Benchmark/Regression + Autonomous Recovery + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T149 (Repair Planner), T033 (Benchmark + Regression), T055 (Autonomous Recovery).
- T001 (Rule 5), T033 (Baseline), T055 (Recovery), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
