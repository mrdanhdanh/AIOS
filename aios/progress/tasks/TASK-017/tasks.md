# TASK-017 — Breakdown

- [x] **17.1** Create governance artifacts (spec, critiques, review, tasks)
- [ ] **17.2** Create `aios/api/__init__.py` + `schemas.py` — Pydantic v2 schemas
- [ ] **17.3** Create `aios/api/errors.py` — Error codes, `ApiError`, handlers
- [ ] **17.4** Create `aios/api/auth.py` — `AuthContext`, API key boundary
- [ ] **17.5** Create `aios/api/contracts.py` — `ApiVersion`, version negotiation
- [ ] **17.6** Create `aios/api/events.py` — `EventService`, whitelist, history
- [ ] **17.7** Create `aios/api/websocket.py` — WebSocket gateway, reconnect
- [ ] **17.8** Create `aios/api/deps.py` — shared router dependencies
- [ ] **17.9** Create `aios/api/app.py` — FastAPI factory, lifespan, OpenAPI
- [ ] **17.10** Create `aios/api/routers/` — 15 routers via RuntimeKernel + PolicyEngine
- [ ] **17.11** Create `aios/api/tests/test_api.py` — ≥80 offline tests
- [ ] **17.12** Run `python -m pytest aios -q` — verify PASS
- [ ] **17.13** Write test.md + evaluation.md + REGRESSION.md
- [ ] **17.14** Update PLAN.md, LOG.md, STATS.md — mark TASK-017 DONE
