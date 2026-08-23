# TASK-136 — Sandbox Manager

## Objective
Triển khai **Sandbox Manager** (M20) như một năng lực có contract, evidence và harness riêng — quản lý vòng đời sandbox (create/destroy/isolate) để execution (T135) chạy isolated, không phá Core. TASK-136 là **sandbox manager, không phải execution mới** (dựa trên Execution Contract T135 + Credential/Network/Sandbox T040 + Resource T005).

## Scope
**In scope:** `aios/execution/sandbox.py` — `SandboxManager`, `SandboxRecord`, `IsolationLevel`, `SandboxStatus`.
**Out of scope:** execution runner mới (T139/T140).

## Deliverables
- `aios/execution/sandbox.py` implementation + lifecycle.
- Unit + Contract + Integration + Architecture + Regression tests (`test_sandbox.py`).
- Tích hợp: T135 -> T136 -> T139/T140.

## Acceptance Criteria
- Sandbox Manager lifecycle create/destroy/isolate đầy đủ.
- `sandbox_id` immutable (T001 Rule 1).
- Isolation process/fs/network hoạt động (T040).
- Sandbox unhealthy -> không chạy execution (T135).
- Mọi lifecycle event có provenance (T001 Rule 5).
- Tích hợp được với Execution Contract + Sandbox + Resource + Evidence.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T135 (Execution Contract) -> T136 -> T139/T140.
- T001 (Rule 1/5), T040 (Sandbox), T005 (Resource), T113 (Policy).

## Governance references
- Rule 1..7 via `aios/governance/*`. `execution` là `unknown` (infra) layer.
