# TASK-002 — Critique 2

## Convergence with Critique 1
Both critiques agree on the core risk areas: config validation, healthcheck
extensibility, and metadata provenance. This second critique adds the following
additional observations.

## Additional Observations
1. **Typing discipline**: All new modules should use `from __future__ import
   annotations` and expose public types via `__all__` for clean import surfaces.
   The governance architecture guard (Rule 3) already scans imports — keeping
   type exports clean helps avoid false positives.
2. **Structured logging format**: JSON-formatted logs are specified, but the
   schema of each log line is not. Define a minimal envelope
   (`timestamp`, `level`, `logger`, `message`, `extra`) so downstream consumers
   (Evidence Store, Audit) can parse logs deterministically.
3. **Healthcheck dependency on config**: The healthcheck module should accept a
   `Config` instance rather than importing global config, keeping it testable
   and consistent with DI principles from TASK-003.
4. **pyproject.toml coverage threshold**: Setting a minimum coverage threshold
   (e.g. 80%) in pyproject.toml prevents coverage regression in later tasks.
5. **No CLI in this task**: The scaffold does not include a CLI entry point.
   This is acceptable — CLI is deferred to a later task. But the package
   structure should leave room for an `aios.cli` subpackage.

## Required Revisions
- Enforce `__all__` exports in all new public modules (done).
- Define log envelope schema in docstring (done).
- Healthcheck accepts `Config` via constructor injection (done).
- Add coverage minimum to pyproject.toml (done).
- Reserve `aios.cli` namespace in package structure (done via existing
  `aios/governance/cli/`).
