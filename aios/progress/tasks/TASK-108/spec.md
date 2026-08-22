# TASK-108 — Management Console / Independent Harness Integration

## Objective
Xây **Management Console Integration cho Independent Harness** — tích hợp independent harness vào management console để operator xem/quản lý independent verification mà không phá Core. Console integration, không phải feature mới (dựa trên Oracle T105 + Foundation T104 + Bridges T106/T107 + Enterprise Ops/Dashboard T042/T072/T018).

## Scope
**In scope:** `aios/independent_harness/console.py` — `ConsoleHarnessView`, `ManagementConsoleIntegration`; `aios/api/routers/independent_harness.py` (router); `aios/dashboard/views.py` (IndependentHarnessView) + tests. Tích hợp Oracle (T105) + Foundation (T104) + Bridges (T106/T107) + Dashboard (T042/T072/T018) + API (T017).
**Out of scope:** console feature mới; provider/filesystem adapters.

## Deliverables
- `aios/independent_harness/console.py` — aggregate + policy-gated action (5 tests).
- `aios/api/routers/independent_harness.py` — REST boundary (register/status/action).
- `aios/dashboard/views.py` — `IndependentHarnessView` (View 11).
- Tests Test Matrix T108.
- Tích hợp Oracle + Foundation + Bridges + Dashboard + API.

## Acceptance Criteria
- Console hiển thị trạng thái independent harness (tổng hợp T105/T106/T107).
- Operator action đi qua API/runtime, không bypass policy (T017/T018).
- **AIOS giữ authority/policy boundary** — console không quyết policy.
- Verdict không xác định → không promote PASS (T078).
- Mọi view có provenance (T001 Rule 5).
- Cùng harness state → cùng view (deterministic).
- Tích hợp được với Oracle + Foundation + Bridges + Dashboard + API.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T104, T105, T106, T107 → T108 → T109 (M17).
- T042/T072/T018 (Dashboard), T017 (API), T078 (Integrity), T001 (Evidence).

## Governance references
- Rule 1..7 via `aios/governance/*`. `independent_harness` là `unknown` layer; router ở `api` layer (được phép import unknown).
