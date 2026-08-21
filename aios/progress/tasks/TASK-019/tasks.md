# TASK-019 — Breakdown

## Steps

1. Create `aios/extension/__init__.py` with public API exports
2. Create `aios/extension/contracts.py` — command definitions, response schemas, diagnostic severity
3. Create `aios/extension/workspace.py` — workspace context adapter (file, selection, git)
4. Create `aios/extension/api_client.py` — extension API client wrapping HTTP calls
5. Create `aios/extension/event_client.py` — real-time event client with reconnection
6. Create `aios/extension/config.py` — extension configuration schema
7. Create `aios/extension/mock_backend.py` — mock backend for offline testing
8. Create `aios/extension/tests/test_contracts.py` — command/response contract tests
9. Create `aios/extension/tests/test_workspace.py` — workspace adapter tests
10. Create `aios/extension/tests/test_api_client.py` — API client tests
11. Create `aios/extension/tests/test_config.py` — config tests
12. Create `aios/extension/tests/test_mock.py` — mock backend tests
13. Run full test suite + architecture gate
