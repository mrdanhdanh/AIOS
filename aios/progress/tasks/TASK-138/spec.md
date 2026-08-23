# TASK-138 — Resource + Network + Command Policy

## Objective
Triển khai **Resource + Network + Command Policy** (M20) như một năng lực có contract, evidence và harness riêng — enforce policy cho resource (cpu/mem), network (egress) và command (allow/deny) trong execution (T135). TASK-138 là **policy enforcement, không phải runner mới** (dựa trên Execution Contract T135 + Credential/Network/Sandbox T040 + Quota/Cost T039 + Permission T035).

## Scope
**In scope:** `aios/execution/policy.py` — `PolicyEngine`, `ExecutionPolicy`, `ResourceLimit`, `PolicyDecision`, `Decision`.
**Out of scope:** runner mới (T139/T140).

## Deliverables
- `aios/execution/policy.py` implementation + fail-closed gate.
- Unit + Contract + Integration + Architecture + Regression tests (`test_policy.py`).
- Tích hợp: T135 -> T138 -> T139/T140.

## Acceptance Criteria
- Resource Policy giới hạn cpu/mem theo quota (T039).
- Network Policy allow/deny egress (T040).
- Command Policy allow/deny command.
- Vi phạm policy -> BLOCK (fail-closed, T078).
- Mọi decision có provenance (T001 Rule 5).
- Cùng policy + request -> cùng decision (deterministic).
- Tích hợp được với Execution Contract + Sandbox + Quota + Permission + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T135 (Execution Contract) -> T138 -> T139/T140.
- T001 (Rule 5), T039 (Quota), T040 (Network), T035 (Permission), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
