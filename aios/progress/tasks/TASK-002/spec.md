# TASK-002 — Monorepo + aios_core Scaffold

## Objective
Create a stable Python monorepo scaffold for the AIOS Runtime. This task
establishes the package layout, configuration, logging, metadata, healthcheck,
and test structure that all subsequent M1 tasks build upon.

## Scope
- **Package layout**: Extend the existing `aios/` namespace into a proper
  `aios_core` package with subpackages for `core`, `runtime`, `harness`, and
  `governance`.
- **Config module** (`aios.core.config`): Centralised, typed configuration with
  environment-variable overrides and sensible defaults.
- **Logging module** (`aios.core.logging`): Structured logging setup with JSON
  formatter, log-level control, and per-module logger factory.
- **Metadata** (`aios.core.metadata`): Package version, build info, and
  capability introspection for runtime self-description.
- **Healthcheck** (`aios.core.healthcheck`): Lightweight health probe that
  aggregates subsystem liveness/readiness and returns a structured result.
- **Test layout**: Dedicated test directories for each subpackage with shared
  fixtures and conftest.
- **pyproject.toml update**: Reflect new package structure, add dev-dependencies
  (pytest, pytest-cov), and configure coverage thresholds.

## Deliverables
- `aios/core/config.py` — typed config with env-var overrides.
- `aios/core/logging.py` — structured logging setup.
- `aios/core/metadata.py` — package metadata + build info.
- `aios/core/healthcheck.py` — health probe aggregation.
- `aios/core/tests/` — unit tests for core modules.
- `aios/runtime/tests/` — placeholder test directory.
- `aios/harness/tests/` — placeholder test directory.
- `aios/conftest.py` — shared fixtures (project root, tmp config).
- Updated `pyproject.toml` with dev-dependencies and coverage config.
- `aios/progress/tasks/TASK-002/` — full lifecycle artifacts.

## Acceptance Criteria
1. **Import smoke**: `python -c "import aios; import aios.core; import aios.core.config; import aios.core.logging; import aios.core.metadata; import aios.core.healthcheck"` succeeds without error.
2. **Config roundtrip**: Creating a `Config()` with defaults and overriding via
   env-var produces the expected values (automated test PASS).
3. **Logging setup**: `setup_logging()` configures root logger and returns a
   module logger; log output respects configured level (automated test PASS).
4. **Metadata**: `PackageMetadata.current()` returns non-empty version, name,
   and python_version fields (automated test PASS).
5. **Healthcheck**: `HealthCheck.run()` returns a `HealthResult` with status
   `HEALTHY` when no probes fail; a failing probe yields `DEGRADED`
   (automated test PASS).
6. **Test suite**: `python -m pytest aios -q` passes with zero failures and
   covers all new modules.
7. **Backward compatibility**: All TASK-001 governance tests continue to pass
   (regression gate).

## Dependencies
- TASK-001 (Task Governance System) — DONE.
