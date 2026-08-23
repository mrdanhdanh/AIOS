# TASK-019 Implementation — VS Code Extension

Implementation lives in `aios/extension/` (M3 Desktop Edition — VS Code Extension).

```
aios/extension/
  contracts.py     # Extension contracts (no business logic, uses AIOS APIs)
  workspace.py     # Workspace integration (file context, diagnostics)
  api_client.py    # API client (REST, typed, contract-based)
  event_client.py  # Event client (WebSocket, real-time)
  config.py        # Extension configuration
  mock_backend.py  # Mock backend for offline tests
  __init__.py      # re-exports
  tests/
    test_extension.py
    test_workspace.py
    test_api_client.py
  src/             # TypeScript VS Code extension (extension/src/ at repo root)
```

Extension contains **no business logic** — all operations go through `aios/api` (REST + WebSocket). Chat, workflow run, task/progress, artifacts, diagnostics all via API.

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (2477 PASS current).
