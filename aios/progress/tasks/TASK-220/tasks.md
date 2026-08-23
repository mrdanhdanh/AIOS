# TASK-220 — Breakdown

1. **CoordinatorAgent** (`aios/agents/coordinator.py`)
   - `CoordinatorAgent` nhận `spec_writer`, `critic`, `reviewer`, `orchestrator` qua constructor (Protocol injection).
   - `coordinate(task_id, spec_input)` chạy pipeline: spec → critique×2 → breakdown → review → orchestrate.
   - `CoordinationResult` / `CoordinationStep` dataclass + `to_dict()`.
   - Fail-closed: review reject → không close.

2. **Exports** (`aios/agents/__init__.py`): thêm `CoordinatorAgent`, `CoordinationResult`, `CoordinationStep`.

3. **Tests** (`aios/agents/tests/test_coordinator.py`): 3 tests (happy path close, fail-closed reject, deterministic).

4. **Chat agent** (`.github/agents/aios-coordinator.agent.md`): `user-invocable: true`, mô tả pipeline + next-step loop.

5. **Evidence & docs**: task artifacts, cập nhật PLAN/LOG/STATS.

6. **Governance**: `gate_check.py --task TASK-220` + `pytest aios -q` (regression closure) → commit Quy tắc 8.
