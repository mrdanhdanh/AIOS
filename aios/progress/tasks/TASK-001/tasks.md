# Breakdown — TASK-001

## Work items
- [x] 1. Edit master spec TASK-001 → governance system design
- [x] 2. Build `aios/governance/` package (8 modules)
- [x] 3. Write automated pytest tests (26 tests)
- [x] 4. `aios/progress/` (PLAN/LOG/STATS, template, TASK-001 folder)
- [x] 5. `docs/PLAN.md`, `AGENTS.md`, `aios/agents/*`
- [x] 6. CLI `parse_spec.py` + `gate_check.py`
- [x] 7. Run tests + regenerate registry + self-gate PASS
- [x] 8. Tự đánh giá & vá fail-open → fail-closed (Dependency/Architecture/Deterministic/Evidence/Regression/Gate/gate_check/EVIDENCE sha256 + docs/PLAN §6)

## Execution plan (deterministic-first)
All steps are deterministic (no LLM control path). Planner/LLM was NOT required. DeterministicControlPath with validator-required enforced.

## Điều chỉnh bổ sung (tự đánh giá)
- DependencyGraph: fail-closed cho unknown task, enforce milestone boundary.
- Architecture: `import os` (Import) + ARCH-004 workflow↔engine + dynamic `__import__`/`importlib`.
- Deterministic: validator REQUIRED khi fallback, thiếu → ControlPathError.
- Evidence: sha256 hash bắt buộc, UNKNOWN never PASS, task-scoped trong TaskGate.
- Regression: exception → BLOCKED.
- TaskGate: evidence lọc theo task_id, regression tự tính closure, thêm deterministic check.
- gate_check.py: đọc STATUS.md thực, hash sha256, không hardcode DONE.
- docs/PLAN.md: bổ sung cột Fail-closed.
