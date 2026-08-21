# TASK-017 — Test Report

## Execution
```
python -m pytest aios/api/tests/test_api.py -q
60 passed

python -m pytest aios -q
1317 passed

python -m pytest aios/governance/architecture -q
112 passed
```

## Per-module
| Module | Tests | Notes |
|--------|-------|-------|
| api/schemas | 4 | Pydantic v2 validation |
| api/errors | 3 | Error model stable schema |
| api/auth | 2 | Auth boundary |
| api/events | 4 | EventService whitelist/history |
| api/contracts | 2 | Version negotiation |
| api/websocket | 2 | ConnectionManager |
| api/app | 1 | Factory |
| api/routers (15) | 36 | All routers tested |
| api/architecture | 2 | Layer guard |
| api/openapi | 2 | Spec validation |
| api/versioning | 2 | Headers |
| **Subtotal** | **60** | |

## Regression
```
python -m pytest aios -q
1317 passed in 6.18s
```
