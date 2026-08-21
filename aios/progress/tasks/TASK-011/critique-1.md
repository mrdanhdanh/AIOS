# TASK-011 — Critique 1 (Spec Review)

## Strengths
- Spec scopes M1 closing gate correctly as remediation, not new feature: contracts + dependency + policy + wiring + invariants + regression.
- Deliverables pin exact files to patch (`guard.py` LAYER_KEYWORDS/ALLOWED_IMPORT_LAYERS, `test_m1_hardening.py` ≥15 tests, `kernel.py` health coverage) — testable and bounded.
- AC-011-01..10 mirror master spec E2E verification (positive simulate + negative POLICY DENY) and Definition of Done workflow, so gate is not satisfiable by ignoring tests.
- Out-of-scope explicitly defers M2 Decision/Worker/Tool/Skill/UI, preventing scope creep.

## Risks / Gaps
- `ALLOWED_IMPORT_LAYERS` tightening must keep backward compat: existing capability tests assert `capability` only imports `tool`/`unknown`; narrowing to `["unknown"]` is stricter and correct for AC-011-04, but must not break `aios/capability` which already avoids runtime imports. Verify with `python -m pytest aios/capability -q`.
- `LAYER_KEYWORDS` extension (`core`,`governance`,`harness`,`kernel`,`progress`) must map to consistent layer or `unknown` so `classify_module` does not mis-classify infra as `tool`/`capability`. Confirm mapping before merge.
- Policy hardening claim needs concrete negative E2E: a workflow requiring forbidden permission → `Policy DENY` → `execution_count==0` with evidence. Test suite must include that path, not only Import/AST checks.
- Kernel `health()` already covers 16 entries; hardening should assert every singleton appears (EventBus + 14 services + Executor wiring) and is `SINGLETON` in Container, or document why an entry is omitted.

## Required revisions
- [x] Lock `agent: ["orchestrator","unknown"]` and `capability: ["unknown"]` in guard.py; keep `unknown` superset to avoid false positives on stdlib/third-party.
- [x] Add `core→unknown`, `governance→unknown`, `harness→unknown`, `kernel→runtime`, `progress→unknown` to LAYER_KEYWORDS with comment explaining backward compat.
- [x] Add ≥15 tests: architecture invariants (ARCH-001..004), capability isolation, workflow compiler isolation, policy pre-check E2E, kernel wiring health, offline simulation.
- [x] Ensure `health()` assertion covers all singletons; add missing counts if any and update STATS.

## Decision
- APPROVE with required revisions addressed — proceed to tasks.md breakdown.
