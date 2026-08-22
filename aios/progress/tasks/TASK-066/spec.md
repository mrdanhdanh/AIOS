# TASK-066 — Durable Execution 1.0

## Objective
Xây dựng **durable execution** cho Runtime: state của execution được checkpoint và có thể resume sau crash / restart mà không mất tiến triển đã verified. T066 tập trung vào **state durability + recovery**, không redesign execution loop.

## Scope
**Trong scope:**
- `Checkpoint` dataclass (execution_id, step_id, state_hash, verified, created_at, evidence_ref).
- `CheckpointStore` (durable): lưu/load checkpoint; persist qua restart (in-memory + optional file-backed).
- `ResumeProtocol`: resume CHỈ từ checkpoint `verified=true` gần nhất (fail-closed).
- `IdempotencyGuard`: không re-execute step đã done (không double side-effect).
- Tích hợp với Runtime state store (T065) và Recovery (T055) qua public interface.

**Ngoài scope:**
- Scheduler mới (thuộc T062/T067).
- Tạo execution store song song (bị cấm — reuse runtime state store).

## Deliverables
- Package `aios/durable/` (`__init__.py`, `checkpoint.py`, `store.py`, `resume.py`, `idempotency.py`, `integration.py`).
- Tests `aios/durable/tests/` phủ mọi AC + Test Matrix.
- Artifacts lifecycle dưới `aios/progress/tasks/TASK-066/`.

## Acceptance Criteria
- AC1: State checkpoint durable (persist qua restart).
- AC2: Chỉ resume từ checkpoint `verified=true`.
- AC3: Resume không gây side-effect kép (idempotency).
- AC4: Checkpoint có provenance evidence.
- AC5: Cùng checkpoint + resume protocol → cùng state (deterministic).
- AC6: Tích hợp được với Runtime (T065) + Recovery (T055).
- AC7: Không tạo execution store song song (reuse runtime state store).
- AC8: Regression của milestone trước PASS; không vi phạm invariants.

## Dependencies
- TASK-065 Runtime Production Hardening (runtime state store: `aios.runtime.state`).
- TASK-055 Autonomous Recovery (contracts: `aios.autonomous_recovery.contracts`).

## Governance references
- Rule 3 (Architecture): `aios/durable/` là layer `unknown`, chỉ import peer (`runtime`, `autonomous_recovery`), không import `agents/`.
- Rule 4/5/6/7 satisfied qua tests + artifacts.
