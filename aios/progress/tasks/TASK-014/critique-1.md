# TASK-014 — Critique 1

## Reviewer: Critic Agent
## Verdict: APPROVE (with notes)

## Strengths
- Spec covers full Tool+Capability boundary: contract, registry, discovery, router, 6 adapters, policy pre-check, health, evidence, offline.
- Layering is explicit: Worker→Capability→Router→Policy→Tool, no bypass.
- Health 5-state (UNKNOWN/HEALTHY/DEGRADED/UNHEALTHY/DISABLED) with fail-closed UNKNOWN is correct per Evidence-First.
- Priority does not override Policy is enforced.
- Offline-first with mock adapters is preserved.

## Issues (non-blocking)
- Ensure ToolRegistry and CapabilityRegistry stay consistent: Tool declares capabilities, CapabilityRegistry maps them — avoid duplicate source of truth. ToolRegistry is master for Tool metadata, CapabilityRegistry for capability identity.
- Router must not become God Object: keep it as resolver (select Tool), not executor. Execution stays in Runtime Execution service.
- Health UNKNOWN must never be promoted to HEALTHY — enforce in router filter.
- Policy pre-check must happen before Tool selection, not after.

## Required revisions (addressed)
- [x] Clarify ToolRegistry vs CapabilityRegistry ownership.
- [x] Router is resolver only, not executor.
- [x] Health UNKNOWN fail-closed.
- [x] Policy pre-check before execution.

## Decision
APPROVE — proceed to critique-2.
