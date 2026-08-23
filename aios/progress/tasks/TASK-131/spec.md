# TASK-131 — Coder Conformance Harness + Security

## Objective
Triển khai **Coder Conformance Harness + Security** (M19) như một năng lực có contract, evidence và harness riêng — validate coder-pipeline artifacts/plans/reports theo invariants M19 (hash, provenance, integrity, deterministic) và enforce security boundary (no forbidden ops, authorized producer). UNKNOWN không bao giờ được promote thành PASS (fail-closed, T078).

## Scope
**In scope:** `aios/coder/conformance.py` — `CoderConformanceHarness`, `ConformanceResult`, `ConformanceStatus`, `SecurityStatus`, `ConformanceError`.
**Out of scope:** autonomy/permission (T132); prompt (T133); file safety (T134).

## Deliverables
- `aios/coder/conformance.py` implementation + contract/schema.
- Unit + Contract + Integration + Architecture + Regression tests trong `aios/coder/tests/test_conformance.py`.
- Tích hợp: T125→T130 -> T131 (M19).

## Acceptance Criteria
- AC của task PASS; UNKNOWN không được nâng thành PASS (fail-closed, T078).
- Evidence có provenance (T001 Rule 5).
- Regression của dependency PASS; không vi phạm invariants.

## Dependencies
- T125..T130 -> T131.
- T001 (Rule 5), T078 (Integrity), T113 (Security).

## Governance references
- Rule 1..7 via `aios/governance/*`. `coder` là `unknown` (infra) layer.
