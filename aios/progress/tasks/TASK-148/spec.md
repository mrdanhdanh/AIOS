# TASK-148 — Diagnostic Agent

## Objective
Triển khai **Diagnostic Agent** (M21) như một năng lực có contract, evidence và harness riêng — chẩn đoán root cause từ failure đã classify (T147) + observation (T146), sinh diagnostic report làm input cho repair planner (T149). TASK-148 là **diagnostic agent, không phải repair mới** (dựa trên Failure Classification T147 + Execution Observation T146 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/diagnostic.py` — `DiagnosticAgent`, `DiagnosticReport`.
**Out of scope:** repair mới (T149).

## Deliverables
- `aios/coding_loop/diagnostic.py` implementation + diagnostic agent.
- Policy Boundary (T113) trên mọi diagnostic.
- Integration với Failure Classification (T147) + Execution Observation (T146) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_diagnostic.py`).

## Acceptance Criteria
- Diagnostic Agent sinh root cause từ class (T147) + observation (T146).
- Diagnostic Report có provenance (T001 Rule 5).
- UNKNOWN (confidence thấp) → không promote PASS (T078).
- Cùng input → cùng root cause (deterministic).
- Diagnostic không lộ secret (T040/T113).
- Tích hợp được với Failure Classification + Execution Observation + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T147 (Failure Classification), T146 (Execution Observation).
- T001 (Rule 5), T078 (Integrity), T040/T113 (Security).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
