# TASK-015 — Breakdown

- [x] **15.1** Create `aios/skill/` package — `__init__.py`, `contracts.py` (SkillContract, SkillDependency, SkillStatus, SkillPersistentState, SkillTransition, validation, checksum, version).
- [x] **15.2** Implement `aios/skill/registry.py` — SkillRegistry (register/get/list/remove, status tracking, thread-safe RLock, duplicate/unknown reject, capability index).
- [x] **15.3** Implement `aios/skill/resolver.py` — SkillDependencyResolver (direct+transitive, version constraints, conflict/cycle detection, topological order, fail-closed).
- [x] **15.4** Implement `aios/skill/sandbox.py` — Sandbox + SandboxPool (lifecycle CREATED→READY→ACQUIRED→RUNNING→RESETTING→READY, FAILED→DESTROY, acquire/release, warm-start, health check, reset, idle eviction, resource/timeout, isolation).
- [x] **15.5** Implement `aios/skill/manager.py` — SkillManager (lifecycle state machine, validate, install, enable/disable, unload/reload, upgrade, rollback, remove, persistence, evidence, policy/permission/capability integration).
- [x] **15.6** Update `aios/governance/architecture/guard.py` — add `skill` layer to LAYER_ORDER/LAYER_KEYWORDS/ALLOWED_IMPORT_LAYERS, forbid skill bypass.
- [x] **15.7** Update `aios/runtime/kernel.py` — wire SkillRegistry + SkillManager + SandboxPool into Container, health snapshot.
- [x] **15.8** Create `aios/skill/tests/` — contract/registry/resolver/manager/sandbox/integration/persistence/rollback/architecture tests (≥80 tests).
- [x] **15.9** Run `python -m pytest aios -q` — verify 1000+ tests PASS, no architecture violations.
- [x] **15.10** Write `test.md` + `evaluation.md` + `regression.md` with evidence.
- [x] **15.11** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-015 DONE.
