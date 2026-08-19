# TASK-002 — Test

## How to run
```
cd d:\AIOS
python -m pytest aios -q
```

## What is covered (43 new automated tests)

| Module | Tests | Coverage |
|--------|-------|----------|
| aios/core/tests/test_config.py | 14 | Config defaults, env-var overrides, validation, helpers |
| aios/core/tests/test_logging.py | 8 | JSONFormatter, TextFormatter, setup_logging, get_logger |
| aios/core/tests/test_metadata.py | 8 | PackageMetadata.current(), BuildInfo, as_dict |
| aios/core/tests/test_healthcheck.py | 8 | Probe registration, healthy/degraded, unregister, Config injection |
| aios/core/tests/test_smoke.py | 5 | Import smoke for all core modules + root |

## Total
- TASK-001 tests: 39
- TASK-002 tests: 43
- **Total suite: 82 tests, 0 failures**
