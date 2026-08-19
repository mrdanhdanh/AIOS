# TASK-002 — Implementation

## Files created / modified

### New modules
- `aios/core/config.py` — typed Config with env-var overrides, fail-closed validation
- `aios/core/logging.py` — JSON/Text structured logging, `setup_logging()`, `get_logger()`
- `aios/core/metadata.py` — `PackageMetadata.current()`, `BuildInfo`, git commit hash
- `aios/core/healthcheck.py` — probe registry, `HealthCheck`, `HealthResult`, `HealthStatus`

### Updated modules
- `aios/core/__init__.py` — exports Config, ConfigError, PackageMetadata, BuildInfo, HealthCheck, HealthResult, HealthStatus
- `aios/__init__.py` — version bump to 0.2.0, milestone M1
- `pyproject.toml` — dev-dependencies, coverage config, package discovery

### Test infrastructure
- `aios/conftest.py` — shared fixtures (project_root, tmp_config)
- `aios/core/tests/__init__.py`
- `aios/core/tests/test_config.py` — 14 tests
- `aios/core/tests/test_logging.py` — 8 tests
- `aios/core/tests/test_metadata.py` — 8 tests
- `aios/core/tests/test_healthcheck.py` — 8 tests
- `aios/core/tests/test_smoke.py` — 5 tests
- `aios/runtime/tests/__init__.py` — placeholder
- `aios/harness/tests/__init__.py` — placeholder

### Governance artifacts
- `aios/progress/tasks/TASK-002/` — spec, critiques, tasks, review, test, evaluation, regression

## Test results
```
82 passed in 0.33s
```
