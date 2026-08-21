# TASK-018 — Breakdown

## Steps

1. Create `aios/dashboard/__init__.py` with public API exports
2. Create `aios/dashboard/client.py` — `DashboardClientProtocol` and `DashboardClient` API wrapper
3. Create `aios/dashboard/websocket_client.py` — WebSocket event client with reconnection
4. Create `aios/dashboard/mock_backend.py` — mock backend implementing same protocol
5. Create `aios/dashboard/health.py` — health status normalization (PASS/WARNING/ERROR/UNKNOWN)
6. Create `aios/dashboard/views.py` — 10 view models (Chat, Workflow, Timeline, Tools, Memory, Artifacts, Skills, Models, Prompts, Health)
7. Create `aios/dashboard/server.py` — dashboard data aggregation server
8. Create `aios/dashboard/tests/test_client.py` — API client tests
9. Create `aios/dashboard/tests/test_views.py` — view model tests
10. Create `aios/dashboard/tests/test_health.py` — health normalization tests
11. Create `aios/dashboard/tests/test_server.py` — server integration tests
12. Create `aios/dashboard/tests/test_mock.py` — mock backend tests
13. Run full test suite + architecture gate
