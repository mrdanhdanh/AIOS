# TASK-106 — Behavioral Conformance Bridge

## Objective
Xây **Behavioral Conformance Bridge** — bridge các behavioral conformance check từ independent harness vào AIOS verification mà không phá Core. Bridge conformance hành vi, không phải feature mới (dựa trên Oracle T105 + Foundation T104 + Behavioral Conformance T089/T090).

## Scope
**In scope:** `aios/independent_harness/behavioral_bridge.py` — `BehavioralConformanceReport`, `BehavioralConformanceBridge` + tests. Tích hợp Oracle (T105) + Foundation (T104) + Behavioral (T089/T090).
**Out of scope:** behavioral feature mới; provider/filesystem adapters.

## Deliverables
- `aios/independent_harness/behavioral_bridge.py` — observation → AIOS conformance (6 tests).
- Tests Test Matrix T106.
- Tích hợp Oracle (T105) + Foundation (T104) + Behavioral (T089/T090).

## Acceptance Criteria
- Behavioral conformance được bridge từ independent harness vào AIOS.
- `conformance` do AIOS quyết; observation không override (authority AIOS).
- Observation không xác định → INCONCLUSIVE → không promote PASS (T078).
- Mọi bridge có provenance (T001 Rule 5).
- Cùng behavior + observation → cùng `conformance` (deterministic).
- Tích hợp được với Oracle + Foundation + Behavioral.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T104, T105 → T106 → T108.
- T089/T090 (Behavioral), T078 (Integrity), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. `independent_harness` là `unknown` layer.
