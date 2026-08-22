# TASK-068 — Breakdown

- [x] Định nghĩa contracts: `HaltSignal`, `HaltSource`, `HaltScope`, `HaltState`,
      `HaltResult`, `DrainResult`, `ExecutionContext`, `HaltViolation`.
- [x] Implement `KillSwitchController`: registry, `is_halted` (authoritative),
      `issue` (broadcast + compliance check + drain + audit), `begin_action` (gate).
- [x] Implement `persistence.py`: `DurablePersistence` + `LocalDurablePersistence`
      (verified state không bị destroy).
- [x] Implement `audit.py`: ghi evidence vào `aios.governance.evidence` với
      provenance chain đầy đủ, idempotent.
- [x] Implement `integration.py`: `GovernorHaltBridge` (T054), fallback T067/T066.
- [x] Viết tests phủ mọi AC + Test Matrix (contracts/controller/integration/audit).
- [x] Chạy `python -m pytest aios/kill_switch -q` → PASS.
- [x] Tạo 9 lifecycle artifacts.
