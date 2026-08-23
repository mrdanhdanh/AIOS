# TASK-146 — Execution Observation

## Objective
Triển khai **Execution Observation** (M21) như một năng lực có contract, evidence và harness riêng — quan sát execution trace/event trong suốt coding loop (T145) để làm input cho failure classification (T147). TASK-146 là **observation layer, không phải classifier mới** (dựa trên Execution Contract T135 + Output/Artifact Collector T141 + Evidence T001).

## Scope
**In scope:** `aios/coding_loop/observation.py` — `ExecutionObservation`, `Observation`, `ObservationStatus`.
**Out of scope:** classifier mới (T147).

## Deliverables
- `aios/coding_loop/observation.py` implementation + observation store.
- Policy Boundary (T113) trên mọi observation.
- Integration với Coding Loop (T145) + Execution Contract (T135) + Collector (T141) + Evidence (T001).
- Unit + Contract + Integration + Architecture + Regression tests (`test_observation.py`).

## Acceptance Criteria
- Observation capture được execution trace (T135) trong suốt loop (T145).
- Mọi observation có provenance chain đầy đủ (T001 Rule 5).
- Cùng execution → cùng trace (deterministic).
- Observation không lộ secret (T040/T113).
- Tích hợp được với Coding Loop + Execution Contract + Collector + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T145 (Coding Loop State Machine), T135 (Execution Contract), T141 (Collector).
- T001 (Rule 5), T040/T113 (Security).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coding_loop` là `unknown` (infra) layer.
