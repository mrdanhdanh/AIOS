# TASK-002 — Monorepo + aios_core Scaffold

## Objective
Tạo skeleton Python/monorepo ổn định làm nền cho Runtime (M1), bao gồm package
layout, config, logging, metadata, healthcheck và test bootstrap.

## Scope
### In scope
- Package layout: `aios/core/`, `aios/runtime/`, `aios/harness/` (skeleton).
- `aios.core` scaffold module: version metadata, structured logging bootstrap,
  `RuntimeConfig` contract, deterministic `healthcheck()`.
- Test bootstrap: `aios/core/tests/test_core.py` + task artifact tests.
### Out of scope
- Runtime service implementations (TASK-004/005).
- Kernel/DI/event-bus (TASK-003).
- Architecture guard repo-wide enforcement (TASK-016).

## Deliverables
- `aios/core/` package (scaffold: metadata, logging, config, healthcheck, tests).
- `aios/runtime/`, `aios/harness/` skeleton packages.
- Task artifact: `implementation/aios_core.py` + `implementation/test_aios_core.py`.
- CI/test bootstrap: pytest discovers `aios/core/tests` and `implementation`.

## Acceptance Criteria
- [x] AC1: `import aios.core` chạy sạch; version metadata đúng (test PASS).
- [x] AC2: `configure_logging()` trả về logger `aios` (test PASS).
- [x] AC3: `RuntimeConfig` có defaults xác định, `as_dict()` (test PASS).
- [x] AC4: `healthcheck()` deterministic, không gọi external (test PASS).
- [x] AC5: layout `aios/core`, `aios/runtime`, `aios/harness` tồn tại (test PASS).
- [x] AC6: pytest bootstrap chạy sạch trên scaffold (test PASS).

## Dependencies / Gate
- Depends on: TASK-001 (governance foundation — registry/state-machine/gate).
- Blocks: TASK-003..TASK-009 (M1 runtime tasks).

## Invariants (General Rules)
- Rule 1 — immutable ID (TASK-002 from master spec).
- Rule 3 — no bypass: scaffold không import os/pathlib/subprocess/provider trực tiếp.
- Rule 4 — deterministic-first: healthcheck/config không gọi LLM.
- Rule 5 — evidence provenance (EVIDENCE.md).
- Rule 6 — lifecycle đầy đủ trước DONE.
- Rule 7 — regression TASK-001 trước PASS.

## Source
- Master spec: `docs/AIOS_Master_Task_Specification_M0-M26.md` (Milestone M1, TASK-002).
