# TASK-011 — Evaluation

## Verdict: PASS

M1 Remediation closes the milestone gate with a minimal, auditable patch set: only `aios/governance/architecture/guard.py` (`LAYER_KEYWORDS` + `ALLOWED_IMPORT_LAYERS`) plus 30 new hardening tests under `aios/governance/architecture/tests/test_m1_hardening.py`. Full regression 544/544 PASS, zero architecture violations.

## Strengths
- Hardening is additive and backward-compatible: `unknown` superset preserved so stdlib/third-party never false-positives; self-import (`agent→agent`, `capability→capability`, `runtime→runtime`) allowed, cross-layer bypass remains blocked.
- E2E verification covered both positive (`simulate_definition` offline, llm=0 tool=0, mock topo) and negative (`Policy DENY → execution 0`) paths per T008-009-011.md §5.
- Kernel health asserts all 17 singleton keys + SINGLETON lifetimes for both runtime and capability registries — wiring verified without behavior change.
- Deterministic guard: pure AST scan, no LLM, offline.

## Risks / Limitations
- `kernel→runtime` / `workflow→runtime` keywords are segment-bound; future `*/kernel_notes.md` prose not scanned as source so safe.
- M1 gate stops at architecture/policy/wiring regression; performance/scale deferred to M6 harness.

## Follow-up
- TASK-010 Decision Pipeline is now unblocked (M1 gate PASS). Next: TASK-010 builds `Request → Normalizer → Rule Engine → Workflow Matcher → Planner LLM → ExecutionPlan` atop this hardened substrate per docs/detailtask/T010.md.

## Evidence
- `python -m pytest aios/governance/architecture/tests/test_m1_hardening.py -q` — 30 passed
- `python -m pytest aios -q` — 544 passed, 0 failed
