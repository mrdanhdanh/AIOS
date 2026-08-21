# TASK-019 — VS Code Extension

## Objective
Build the Python backend contracts and client layer for a VS Code extension that interacts with AIOS. The extension is a thin client — all business logic lives in the AIOS backend. This task creates the extension contracts, workspace adapter, and API client that any VS Code extension (TypeScript or Python) would consume.

## Scope
### In scope
- Extension command contracts (Chat, Explain, Fix, Generate Test, Review, Refactor, Rename, Ask Workspace)
- Workspace context adapter (file selection, open files, git state)
- API client for extension-backend communication
- Event client for real-time updates
- Policy integration for workspace actions
- Mock extension backend for testing
- Extension configuration schema

### Out of scope
- TypeScript/JavaScript VS Code extension package (separate build)
- Marketplace publishing
- Authentication UI (M7 scope)
- Multi-tenant workspace isolation (M7 scope)

## Deliverables
- `aios/extension/__init__.py` — public API
- `aios/extension/contracts.py` — command definitions and response schemas
- `aios/extension/workspace.py` — workspace context adapter
- `aios/extension/api_client.py` — extension API client
- `aios/extension/event_client.py` — real-time event client
- `aios/extension/config.py` — extension configuration
- `aios/extension/mock_backend.py` — mock backend for testing
- `aios/extension/tests/` — comprehensive tests

## Acceptance Criteria
- AC-019-01: Commands map to correct AIOS API endpoints
- AC-019-02: No orchestration/business logic in extension layer
- AC-019-03: Workspace context respects Policy
- AC-019-04: No direct Runtime/Tool access
- AC-019-05: Task/progress data from backend
- AC-019-06: Artifact provenance preserved
- AC-019-07: Diagnostics show correct severity/state
- AC-019-08: Offline deterministic path works
- AC-019-09: Extension reconnects with backend
- AC-019-10: No parallel state authority

## Dependencies
- TASK-017 (FastAPI REST + WebSocket)

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
