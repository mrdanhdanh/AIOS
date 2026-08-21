# TASK-014 — Evaluation

## Verdict: PASS

Tool + Capability Layer meets spec in full. Tool Contract with 6 types and 5 health states, Tool Registry with dynamic Capability→Tool[] discovery, 6 offline mock adapters, Capability Router with health/priority/policy routing, fail-closed UNKNOWN, evidence with resolution reason, and RuntimeKernel wiring. 163 new tests + 851 inherited = 1014 total, 0 failed. Architecture Guard clean.

## Strengths
- Tool Contract is versioned via `aios.core.contracts` + `aios.core.version`, with 6 ToolTypes and 5 health states; UNKNOWN fail-closed (never promoted to healthy) per Evidence-First.
- Tool Registry builds Capability→Tool[] dynamically from Tool declarations, no hard-code Agent→Tool; multi-tool capability with priority desc + seq tie-break deterministic.
- 6 adapters (Python/Docker/REST/MCP/Shell/Git) are offline mocks — no subprocess, no network, no Docker, no Git — tests run without Internet; each declares capabilities and returns standardized ToolResult with evidence_ref.
- Capability Router is resolver only (not executor): health filter (HEALTHY/DEGRADED eligible, UNHEALTHY/DISABLED/UNKNOWN reject), priority selection (higher wins, not override Policy), Policy pre-check (ALLOW/DENY/ASK, DENY skip to next, ASK no auto-execute), constraints (tool_type/sandbox/network), fail-closed UNRESOLVED, evidence with candidates/reason.
- Policy boundary: Tool does not bypass Policy (adapters never import PolicyEngine), Router checks Policy before selection, priority never overrides DENY, fallback only when policy allows.
- Worker isolation: Worker/Agent never import Tool directly (verified by AST architecture tests); Tool layer only imports core/stdlib; Router at runtime layer.
- RuntimeKernel wires ToolRegistry + CapabilityRouter as singletons with shared PolicyEngine, health snapshot includes tools.

## Risks / Limitations
- Tool execution is mock (no real Python/Docker/REST/MCP/Shell/Git execution); real execution deferred to TASK-015 Sandbox Pool and actual adapters.
- CapabilityRegistry health extended to 5-state but existing tests still use healthy/unhealthy; full 5-state coverage is in new ToolRegistry/Router tests.
- Router constraints are minimal (tool_type/sandbox/network); richer constraints (language, resources) deferred to TASK-015/025.
- Persistence is in-memory; no DB or distributed storage (deferred to M7).

## Follow-up
- TASK-015 Plugin / Skill Execution will provide Sandbox Pool and real Tool execution with resource isolation.
- TASK-016 Architecture Hardening will add cross-task architecture gate over Tool+Capability layer.
- TASK-025 Model Router will extend routing with model selection.

## Evidence
- `python -m pytest aios/tool -q` — 156 passed
- `python -m pytest aios/runtime/tests/test_capability_router.py -q` — 7 passed
- `python -m pytest aios -q` — 1014 passed, 0 failed
- Architecture Guard: `python -m pytest aios/tool/tests/test_architecture.py -q` — 8 passed, 0 violations
- Tool layer classification: `classify_module("aios/tool/contracts.py") == "tool"` verified
- Router layer classification: `classify_module("aios/runtime/capability_router.py") == "runtime"` verified
