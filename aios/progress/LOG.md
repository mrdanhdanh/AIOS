# AIOS Progress Log

Append-only. Each entry: `## [YYYY-MM-DD] session — <topic>`.

## [2026-08-19] session — Vá lỗi template STATUS.md gây lập lại quy trình
- Triệu chứng: mọi task mới (TASK-002, TASK-003…) tạo bằng `Copy-Item _TEMPLATE` đều kẹt
  ở gate `lifecycle` với giá trị `state=` rác (`PLANNED | SPEC | CRITIQUE | ... | CLOSED`).
- Nguyên nhân: `_TEMPLATE/STATUS.md` ghi `state:` là **menu tên cũ** (không khớp enum của
  `aios/governance/lifecycle/statemachine.py`: PLANNED/SPECIFIED/CRITIQUED_1/.../DONE).
  `gate_check.py::_parse_status_file` đọc dòng `state:` đẩy thẳng vào `TaskStateMachine` →
  state không hợp lệ → lifecycle FAIL → agent sửa→chạy lại→FAIL → **lập đi lập lại**.
- Vá: `_TEMPLATE/STATUS.md` (và `TASK-002/STATUS.md` vừa copy) đổi `state:` thành `PLANNED`
  (single valid value) + chú thích enum. Sau vá: `gate_check.py TASK-002` báo
  `state=PLANNED` sạch, FAIL đúng lý do (thiếu artifact) thay vì parse lỗi.
- Kế tiếp: chạy TASK-002 qua vòng đời (SPECIFIED→CRITIQUED_1→...→DONE) không bị kẹt nữa.
- TODO (không block): `STATS.md`/`LOG.md` vẫn là template chưa tính metrics; cân nhắc script
  `new_task.py` scaffold tự động từ `_TEMPLATE` để tránh copy thủ công.

## [2026-08-19] session — Governance foundation
- Read & evaluated `docs/AIOS_Master_Task_Specification_M0-M26.md` (218 tasks, M0–M26).
- Gap: the 7 General Rules are *declared* in the spec but not yet *operationalized*
  (no PLAN.md, no AGENTS.md, no agent roles, no task folders, no gate, no registry).
- Built TASK-001 governance foundation:
  - `docs/PLAN.md` (operational source of truth)
  - `AGENTS.md` (hard-gate workflow for agents/sessions)
  - `aios/agents/` roles: orchestrator, spec-writer, critic, reviewer
  - `aios/progress/` system + `_TEMPLATE/` (per-task folder standard + EVIDENCE/REGRESSION/STATUS)
  - `aios/scripts/parse_spec.py` (Rule 1/2) + `gate_check.py` (unified gate)

## [2026-08-19] session — TASK-001 → Task Governance System
- Revised TASK-001 in master spec to become the self-verifying Task Governance System
  (per pasted design): 7 components, unified gate, Phase A/B/C order.
- Built `aios/governance/` package — real, tested enforcement of all 7 rules:
  - `task_registry` (R1) · `dependency` (R2) · `architecture` (R3) · `deterministic` (R4)
  - `evidence` (R5) · `lifecycle` (R6) · `regression` (R7) · `gates` (unified)
  - 26 automated pytest tests → **all PASS**.
- `parse_spec.py` generated `task-registry.json` + `task-index.md`: **218 tasks / 27 milestones**
  (proves Rule 1 uniqueness + Rule 2 milestone derivation on the real spec).
- Executed TASK-001 through the full lifecycle in `aios/progress/tasks/TASK-001/` and ran
  `gate_check.py TASK-001` → **DECISION: DONE (exit 0)**. Phase B proof complete.

## [2026-08-19] session — TASK-002 → Monorepo + aios_core Scaffold (M1)
- Thực hiện lại TASK-002 trọn vòng đời (spec → critique×2 → tasks → review → implementation
  → test → evaluation → EVIDENCE → REGRESSION → STATUS=DONE).
- Deliverable thực tế:
  - `aios/core/` package: `scaffold.py` (version metadata, `configure_logging`,
    `RuntimeConfig`, deterministic `healthcheck`), `__init__.py`, `tests/test_core.py`.
  - `aios/runtime/__init__.py`, `aios/harness/__init__.py` — skeleton packages.
  - Task artifact `implementation/aios_core.py` (re-export, Rule 3 compliant: không import
    os/pathlib/subprocess/provider) + `implementation/test_aios_core.py` (string-only path).
- Tuân thủ Rule 3: scaffold chỉ dùng logging/sys/dataclasses/typing; Rule 4: healthcheck/config
  deterministic, không LLM.
- Test: `pytest aios/core/tests + implementation` → **7 passed**.
- `gate_check.py TASK-002` → **DECISION: DONE (exit 0)** (registry/dependency/architecture/
  evidence/lifecycle/regression đều PASS).
- Regression: re-run TASK-001 governance tests + gate (REGRESSION.md).
- Next: TASK-002 (Phase C) must now run through the same governance gate.

## [2026-08-19] session — TASK-001 tự đánh giá & vá fail-closed
- Audit toàn bộ `aios/governance/` (32 file, 26 test) phát hiện 4 điểm fail-open: dependency swallow exception, architecture `import os` lọt, deterministic thiếu validator, evidence `n/a`/`UNKNOWN` vẫn PASS, gate evidence cross-task, `gate_check.py` hardcode DONE.
- Vá: `dependency/graph.py` (fail-closed + milestone boundary), `architecture/rules.py` (ARCH-002 Import + ARCH-004 + dynamic import), `deterministic/path.py` (validator REQUIRED), `evidence/store.py` (sha256 bắt buộc, UNKNOWN never PASS), `regression/runner.py` (exception→BLOCKED), `gates/gate.py` (task-scoped evidence + tự tính regression + deterministic check), `scripts/gate_check.py` (đọc STATUS.md thực, hash sha256), `EVIDENCE.md` (sha256 thật), `docs/PLAN.md` §6 (cột Fail-closed).
- Kiểm chứng: `pytest aios/governance -q` → 26 passed; `gate_check.py TASK-001` → DONE.
