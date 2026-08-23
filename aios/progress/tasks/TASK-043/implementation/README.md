# TASK-043 Implementation — Public AIOS SDK

Implementation lives in `aios/sdk/` (M8 Ecosystem — Public SDK).

```
aios/sdk/
  contracts.py   # SDKConfig, SDKResponse, ErrorCode, SDKError, SDKVersion
  client.py      # AIOSClient (health, execute, list_resources, config)
  discovery.py   # Service discovery
  mock_client.py # MockAIOSClient (offline, no network)
  __init__.py    # re-exports
  tests/
    test_sdk.py
    test_discovery.py
```

Stable, versioned, contract-first SDK. Error model with provenance. Offline-capable via `MockAIOSClient`.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2519 PASS current).
