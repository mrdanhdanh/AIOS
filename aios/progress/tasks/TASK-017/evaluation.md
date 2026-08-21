# TASK-017 — Evaluation

## AC Verification

| AC | Description | Status |
|----|-------------|--------|
| AC-017-01 | Shared contracts via OpenAPI (versioned, `/api/v1`) | PASS — 39 paths in OpenAPI spec |
| AC-017-02 | REST not bypass Policy (DENY → 403) | PASS — `test_policy_deny` |
| AC-017-03 | WebSocket whitelist events only | PASS — `ALLOWED_EVENTS` enforced |
| AC-017-04 | Execution state = StateStore | PASS — `test_create`, `test_get`, `test_state` |
| AC-017-05 | Stable error schema | PASS — `test_error_model` (404/422/500) |
| AC-017-06 | API versioning `/api/v1` + header | PASS — `test_version_header` |
| AC-017-07 | No implementation detail exposed | PASS — `test_no_internal_detail` |
| AC-017-08 | WebSocket reconnect via `last_event_id` | PASS — `replay_since()` in `EventService` |
| AC-017-09 | Offline tests (no LLM, no network) | PASS — all 60 tests offline |
| AC-017-10 | `api` layer guard correct | PASS — `test_api_layer_no_reverse_import` |
| AC-017-11 | OpenAPI auto-generated | PASS — `test_openapi_spec`, `test_all_routers_present` |
| AC-017-12 | Full regression PASS | PASS — 1317 tests |

## Verdict: ALL AC PASS
