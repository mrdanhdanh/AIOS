# TASK-220 — AIOS Coordinator Agent (control-plane prototype + chat agent)

## Objective
Xây **CoordinatorAgent** — một agent tầng `agents` (pure, I/O-free, capability-injected)
điều phối các agent vai trò khác (`SpecWriter`, `Critic`, `Reviewer`, `Orchestrator`)
qua pipeline governance: `spec → critique×2 → breakdown(tasks) → review → orchestrate/close`.
Đồng thời đóng gói một **custom chat agent** (`.agent.md`) để người dùng chọn từ
dropdown chat VS Code và agent tự biết bước tiếp theo. Tất cả tuân thủ phân tầng
`Agent → Orchestrator → Runtime → Capability → Tool` và 7-gate fail-closed.

## Scope
**In scope:**
- `aios/agents/coordinator.py` — `CoordinatorAgent`, `CoordinationResult`, `CoordinationStep`.
- `aios/agents/__init__.py` — export mới.
- `aios/agents/tests/test_coordinator.py` — 3 tests (happy path, fail-closed, deterministic).
- `.github/agents/aios-coordinator.agent.md` — custom chat agent (VS Code picker).
- Task artifacts + evidence.

**Out of scope:** tự động hóa terminal/chat server riêng; nối vào FastAPI endpoint;
auto-commit tự động (thuộc Quy tắc 8 thủ công).

## Deliverables
- `aios/agents/coordinator.py` — agent điều phối, deterministic + fail-closed.
- `aios/agents/__init__.py` — thêm export `CoordinatorAgent`, `CoordinationResult`, `CoordinationStep`.
- `aios/agents/tests/test_coordinator.py` — 3 tests passed.
- `.github/agents/aios-coordinator.agent.md` — chat agent, `user-invocable: true`.
- Cập nhật `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` + commit `TASK-220: ... — DONE`.

## Acceptance Criteria
- `CoordinatorAgent` nhận 4 sub-agent qua injection (Protocol), không import `subprocess`/`os`/provider/filesystem (ARCH-001..004).
- Pipeline sinh đủ artifact keys: `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`.
- Khi `Reviewer` reject → `result.approved=False` và `result.closed=False` (fail-closed, không close).
- Cùng input → cùng `result.to_dict()` (deterministic).
- `python -m pytest aios/agents/tests/test_coordinator.py -q` → 3 passed.
- Architecture gate quét `aios/agents` → không vi phạm ARCH-001..004.
- `.github/agents/aios-coordinator.agent.md` có `description` + `tools` + `user-invocable: true`, xuất hiện trong agent picker.
- Regression closure: `python -m pytest aios -q` không break (toàn bộ suite).

## Dependencies
- T001 (lifecycle + gates), T008 (workflow CLI), T125 (coder contract pattern tham khảo).
- `aios/agents/{orchestrator,spec_writer,critic,reviewer}.py` (đã DONE).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `coordinator` ở `agents` layer; import `aios.governance` (unknown, allowed) + `aios.agents.*` (peer). Cấm `subprocess`/`os` (ARCH-001).
- Quy tắc 8: khi DONE → commit `TASK-220: AIOS Coordinator Agent — DONE` + update PLAN/LOG/STATS.
