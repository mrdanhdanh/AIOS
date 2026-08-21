# TASK-011 — Critique 2 (Architecture & Test Review)

## Strengths
- Guard patch is minimal and auditable: only `LAYER_KEYWORDS` and `ALLOWED_IMPORT_LAYERS` change, scanner logic untouched.
- New hardening tests are placed under `aios/governance/architecture/tests/test_m1_hardening.py` — co-located with the gate, not scattered.
- Kernel health already deterministic and offline; hardening only asserts completeness, no behavior change.

## Risks / Gaps
- `kernel` keyword could appear in many non-runtime paths (e.g., `aios/progress/tasks/.../kernel.md` prose). Mapping `kernel → runtime` is correct for `aios/runtime/kernel.py` but must be word-boundary on path segments (already is — `classify_module` splits on `/`), so false positives are avoided. Confirm with a negative test: `classify_module("docs/kernel_notes.md") → runtime` is acceptable since it is not scanned as source.
- Agent tightening to `["orchestrator","unknown"]` means an agent importing `runtime` directly will now violate ARCH-004, which is the intent of AC-011-04. Ensure existing `aios/agents/orchestrator.py` (which imports governance only) still passes — it does (`unknown`).
- Test count ≥15 must cover AC-011-02,03,04,05 distinctly, not just parametric copies. Need separate test functions for invariants, policy pre-check, workflow isolation, agent boundary plus kernel/health/contract checks.

## Required revisions
- [x] Add explicit tests: `test_agent_cannot_import_tool_directly`, `test_capability_cannot_import_runtime`, `test_workflow_no_langgraph_import`, `test_policy_denies_execution_without_permission`, `test_health_covers_all_singletons`, `test_m1_offline_simulation_llm_zero`, plus ARCH-001..004 parametric coverage to reach ≥15.
- [x] Keep `unknown` in every allow-list so stdlib/third-party never triggers ARCH-004.
- [x] Verify `python -m pytest aios/governance/architecture -q` still green after tightening.

## Decision
- APPROVE with required revisions addressed — proceed to review.
