# TASK-068 — Kill Switch (emergency stop)

## Objective
Xây dựng cơ chế dừng khẩn cấp (Kill Switch) toàn cục, fail-closed, để dừng mọi
autonomous execution một cách đáng tin cậy. Đây là **global halt mechanism**,
không phải autonomy policy (dựa trên T067 Autonomy Safety + T054 Governor).

## Scope
- Trong scope: `HaltSignal`, `KillSwitchController`, halt propagation, graceful
  drain + persist (durable), halt state + audit evidence, tích hợp Governor (T054).
- Ngoài scope: autonomy policy/risk scoring (thuộc T054/T067), SLO/reliability
  (T069). `autonomy_safety` (T067) và `durable` (T066) chưa tồn tại trong
  workspace → dùng local fallback (stub / in-memory persistence).

## Deliverables
- Package `aios/kill_switch/` (`__init__.py`, `contracts.py`, `controller.py`,
  `audit.py`, `persistence.py`, `integration.py`).
- `HaltSignal` dataclass (source/scope/issued_at/reason/evidence_ref).
- `KillSwitchController.issue()` broadcast tới mọi active loop/goal, fail-closed.
- Graceful drain + persist state (durable) trước khi dừng; không action mới.
- Halt state + audit evidence (provenance qua `aios.governance.evidence`).
- Tích hợp Governor (T054) qua `GovernorHaltBridge`; bridge T067/T066 optional.
- Tests pytest phủ mọi AC + Test Matrix.

## Acceptance Criteria
- AC1: Halt được mọi layer tôn trọng (fail-closed, không ignore).
- AC2: Halt không phá hủy state đã verified (durable).
- AC3: Graceful drain — không action mới, persist in-flight.
- AC4: Mọi halt ghi audit evidence (provenance đầy đủ).
- AC5: Cùng halt signal + state → cùng hành vi (deterministic).
- AC6: Tích hợp được với Governor (T054) (+ T067/T066 optional).
- AC7: Không layer nào bypass halt (skip → blocked fail-closed).
- AC8: Regression milestone trước PASS; không vi phạm invariants.

## Dependencies
- TASK-054 Autonomy Governor (tồn tại, tích hợp trực tiếp).
- TASK-066 Durable (chưa tồn tại → local fallback).
- TASK-067 Autonomy Safety (chưa tồn tại → local stub).

## Governance references
- Rule 3 (Architecture): `kill_switch` là layer `unknown`, chỉ import peer
  (`autonomy_governor`, `governance.evidence`), không import `agents/`.
- Rule 5 (Evidence): mọi halt ghi evidence có provenance chain đầy đủ.
- Rule 6 (Lifecycle): 9 artifacts theo chuẩn `_TEMPLATE`.
