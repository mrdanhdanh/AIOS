# TASK-068 Implementation

Real source code lives in the package **`aios/kill_switch/`** (not here — this
directory is only a pointer per the lifecycle standard).

## Modules
| Module | Responsibility |
|--------|----------------|
| `aios/kill_switch/contracts.py` | `HaltSignal`, `HaltSource`, `HaltScope`, `HaltState`, `HaltResult`, `DrainResult`, `ExecutionContext` (Protocol), `HaltViolation`. |
| `aios/kill_switch/controller.py` | `KillSwitchController`: registry of active contexts, `issue()` (broadcast + fail-closed compliance + graceful drain + audit), `begin_action()` gate. |
| `aios/kill_switch/persistence.py` | `DurablePersistence` interface + `LocalDurablePersistence` (in-memory; verified state never destroyed). Stand-in for T066 Durable. |
| `aios/kill_switch/audit.py` | `AuditLog`: records every halt as admissible evidence with full provenance via `aios.governance.evidence`. |
| `aios/kill_switch/integration.py` | `GovernorHaltBridge` (T054), `build_durable_persistence()` (T066 fallback), `build_safety_bridge()` (T067 fallback). |
| `aios/kill_switch/tests/` | pytest covering every AC + Test Matrix row. |

## Integration notes
- **T054 Governor** (exists): `GovernorHaltBridge` wraps `AutonomyGovernor.gate`
  and returns `BLOCK` fail-closed when halted.
- **T066 Durable** (not present): `build_durable_persistence()` falls back to
  `LocalDurablePersistence`. Swap in `aios.durable.DurableStore` when available.
- **T067 Autonomy Safety** (not present): `build_safety_bridge()` falls back to
  a local stub whose `is_safe()` reflects the halted state.

## Architecture
`kill_switch` is classified as an `unknown` layer by the architecture guard, so
peer imports of `autonomy_governor` / `governance.evidence` are allowed and no
`agents/` / `subprocess` / `os` imports are used.
