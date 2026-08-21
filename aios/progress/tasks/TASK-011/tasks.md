# TASK-011 — Breakdown

- [x] **11.1** Create `aios/progress/tasks/TASK-011/` scaffold — `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`, `review.md` per `_TEMPLATE`.
- [x] **11.2** Patch `aios/governance/architecture/guard.py` — extend `LAYER_KEYWORDS` with `core→unknown`, `governance→unknown`, `harness→unknown`, `kernel→runtime`, `progress→unknown`; tighten `ALLOWED_IMPORT_LAYERS` (`agent: ["orchestrator","unknown"]`, `capability: ["unknown"]`), keep `unknown` superset for backward compat.
- [x] **11.3** Verify `aios/runtime/kernel.py` health covers all singletons (EventBus + 14 services + Executor) — no code change needed, add assertions in hardening tests.
- [x] **11.4** Create `aios/governance/architecture/tests/test_m1_hardening.py` — ≥15 tests covering AC-011-02 (ARCH-001..004 invariants), AC-011-03 (policy pre-check DENY→execution 0), AC-011-04 (agent boundary no Tool/provider/filesystem), AC-011-05 (workflow no langgraph/jinja2), plus kernel/contract/offline checks.
- [x] **11.5** Run targeted suites: `python -m pytest aios/governance/architecture -q`, `aios/capability -q`, `aios/runtime -q`.
- [x] **11.6** Run full regression `python -m pytest aios -q` — verify ≥514 PASS, zero architecture violations.
- [x] **11.7** Write `test.md` + `evaluation.md` + `REGRESSION.md` with evidence (pytest tallies, gate outputs).
- [x] **11.8** Update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` — mark TASK-011 `DONE` (544 tests, M1 gate PASS).
