# TASK-147 — Failure Classification

## Objective
Triển khai **Failure Classification** (M21) như một năng lực có contract, evidence và harness riêng — phân loại failure từ observation (T146) theo một taxonomy xác định, deterministic, làm input cho diagnostic agent (T148). TASK-147 là **classifier, không phải diagnostic mới** (dựa trên Execution Observation T146 + Execution Contract T135 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/classification.py` — `FailureClassifier`, `FailureClass`, `FailureTaxonomy`, `CONFIDENCE_THRESHOLD`.
**Out of scope:** diagnostic mới (T148).

## Deliverables
- `aios/coding_loop/classification.py` implementation + classifier.
- Policy Boundary (T113) trên mọi classification.
- Integration với Execution Observation (T146) + Execution Contract (T135) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_classification.py`).

## Acceptance Criteria
- Classification có taxonomy xác định, đóng.
- Observation (T146) → class failure xác định.
- UNKNOWN (confidence thấp) → không promote PASS (T078).
- Mọi classification có provenance (T001 Rule 5).
- Cùng observation → cùng class (deterministic).
- Tích hợp được với Execution Observation + Execution Contract + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T146 (Execution Observation), T135 (Execution Contract).
- T001 (Rule 5), T078 (Integrity).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
