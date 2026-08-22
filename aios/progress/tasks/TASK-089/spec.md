# TASK-089 — Behavioral Conformance

## Objective
Thiết lập **Behavioral Conformance** — định nghĩa và kiểm tra *hành vi* (behavior)
của hệ thống theo các kịch bản quan sát được, đảm bảo AIOS 1.x hành xử đúng theo
spec hành vi (không chỉ contract). TASK-089 là **behavioral spec + conformance,
không phải runtime feature** (dựa trên Harness T030/T032 + Evidence T001 + Conformance T087).

## Scope
**In scope:** `aios/behavioral/` — BehaviorScenario, BehaviorHarness,
BehaviorConformanceChecker, BehaviorConformanceResult. Tích hợp Harness (T030/T032)
+ Evidence (T001) + Conformance (T087).
**Out of scope:** thay thế runtime; provider/filesystem adapters; agent-layer imports.

## Deliverables
- `aios/behavioral/behavioral.py` — scenario + harness + conformance checker.
- `aios/behavioral/tests/test_behavioral.py` — 9 tests (Test Matrix).
- Tích hợp với Harness (T030/T032) + Evidence (T001) + Conformance (T087).

## Acceptance Criteria
- Behavior Spec định nghĩa kịch bản observable (given/when/then).
- Behavior Harness drive + observe được.
- Behavior lệch expected → không conform (fail-closed).
- Spec dựa trên observable (không nội tâm).
- Mọi behavior run có provenance (T001 Rule 5).
- Cùng scenario + system → cùng observable (deterministic).
- Tích hợp được với Harness + Evidence + Conformance.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T088 (Docs & ADR) → T089 → T090.
- T030/T032 (Harness), T001 (Evidence), T087 (Conformance).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `behavioral` là `unknown`
  layer; chỉ import stdlib + `aios.harness` + `aios.governance.evidence` + `aios.conformance`.
