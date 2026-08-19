# TASK-003 — Kernel Foundations

## Objective
Build the kernel-level primitives that every AIOS runtime service depends on:
semantic versioning, typed contracts with schema compatibility, a dependency
injection container, and an in-process event bus. These four pillars let later
tasks (TASK-004+) wire services together without tight coupling.

## Scope
- **Semantic versioning** (`aios.core.version`): parse, compare, and validate
  `MAJOR.MINOR.PATCH` strings per SemVer 2.0.
- **Contracts** (`aios.core.contracts`): typed interface definitions with
  version metadata; compatibility checker that compares required vs provided
  contract versions.
- **DI Container** (`aios.core.container`): register and resolve services by
  type with three lifetimes: `singleton`, `scoped`, `transient`.
- **Event Bus** (`aios.core.events`): in-process publish/subscribe with
  typed events, wildcard listeners, and synchronous dispatch.
- **Execution Plan Primitives** (`aios.core.planner`): lightweight data
  structures (`ExecutionPlan`, `Step`, `StepStatus`) that later planning
  tasks extend.

## Deliverables
- `aios/core/version.py` — semantic versioning.
- `aios/core/contracts.py` — typed contracts + compatibility checker.
- `aios/core/container.py` — DI container with singleton/scoped/transient.
- `aios/core/events.py` — event bus with typed events.
- `aios/core/planner.py` — execution plan primitives.
- `aios/core/tests/test_version.py` — versioning tests.
- `aios/core/tests/test_contracts.py` — contract compatibility tests.
- `aios/core/tests/test_container.py` — DI container tests.
- `aios/core/tests/test_events.py` — event bus tests.
- `aios/core/tests/test_planner.py` — planner primitive tests.

## Acceptance Criteria
1. **Version parsing**: `SemVer.parse("1.2.3")` succeeds; invalid strings raise
   `VersionError` (automated test PASS).
2. **Version comparison**: `SemVer("1.0.0") < SemVer("2.0.0")` and
   `SemVer("1.0.0") < SemVer("1.1.0")` hold (automated test PASS).
3. **Contract compatibility**: compatible versions resolve; incompatible versions
   raise `ContractError` (automated test PASS).
4. **DI singleton**: same instance returned on repeated resolution
   (automated test PASS).
5. **DI scoped**: new instance per scope (automated test PASS).
6. **DI transient**: new instance every resolution (automated test PASS).
7. **Event bus publish/subscribe**: subscriber receives event; order preserved
   (automated test PASS).
8. **Execution plan**: `ExecutionPlan` tracks steps and status transitions
   (automated test PASS).
9. **Test suite**: `python -m pytest aios -q` passes with zero failures.
10. **Backward compatibility**: All TASK-001 + TASK-002 tests continue to pass
    (regression gate).

## Dependencies
- TASK-002 (Monorepo + aios_core Scaffold) — DONE.
