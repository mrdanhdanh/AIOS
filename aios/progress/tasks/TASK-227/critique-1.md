# Critique 1 — TASK-227

- Spec is concrete; AC map to deterministic behavior.
- `StubGuard` belongs in `aios/runtime/` (ARCH-003 compliant). Agents must not import it directly — receive via capability injection.
- Consider wiring: orchestrator loop calls `stub_guard.record(step, status)` after each step and checks `is_clean()` before claiming DONE.
