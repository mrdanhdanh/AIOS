# TASK-002 — Breakdown

- [x] **2.1** Implement `aios/core/config.py` — typed Config with env-var overrides + validation
- [x] **2.2** Implement `aios/core/logging.py` — structured JSON logging setup + module logger factory
- [x] **2.3** Implement `aios/core/metadata.py` — PackageMetadata with version, name, python_version, commit_hash
- [x] **2.4** Implement `aios/core/healthcheck.py` — probe registry + HealthCheck + HealthResult
- [x] **2.5** Create `aios/conftest.py` — shared fixtures (project_root, tmp_config)
- [x] **2.6** Update `pyproject.toml` — dev-dependencies, coverage config, new package paths
- [x] **2.7** Create `aios/core/tests/` — unit tests for config, logging, metadata, healthcheck
- [x] **2.8** Create `aios/runtime/tests/` and `aios/harness/tests/` — placeholder directories
- [x] **2.9** Update `aios/core/__init__.py` — export new public API
- [x] **2.10** Update `aios/__init__.py` — bump milestone marker to M1
- [x] **2.11** Run full test suite — all TASK-001 + TASK-002 tests green (82 passed)
- [x] **2.12** Write regression.md — verify TASK-001 dependency closure green
