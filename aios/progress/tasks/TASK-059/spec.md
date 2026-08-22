# TASK-059 — Multi-Agent Autonomy (Delegation)

## Objective
Build a **delegation capability** extending the existing Orchestrator (Agent Selector / Capability Router) so an agent can delegate sub-goals to child agents/capabilities with multi-dimensional authority attenuation, bounded resources, scope isolation, delegation provenance, and fail-closed recovery. It is NOT a multi-agent framework or second control plane.

## Scope
### In scope
- `Authority` (multi-dimensional): capability scope, resource budget, deadline, tenant/project/workspace scope, tool/network permission, approval requirement, delegation depth, risk level.
- `DelegateRequest` / `DelegateResponse` protocol (attenuated_authority + 3 budgets: execution/delegation/authority).
- `AuthorityAttenuator`: child = Parent ∩ Delegation Scope ∩ Policy ∩ Resource Budget (never inherited wholesale).
- Anti-amplification guard: child authority ⊆ parent; cumulative downstream ≤ parent commitment.
- Bounded limits: delegation depth, child count, delegation budget, cumulative resource, retries, concurrency.
- Delegation Provenance Chain (replay/audit via Evidence Store).
- Parent accountability: parent owns aggregated outcome; child evidence propagates up.
- Child architecture boundary (ARCH-001/002/003/004): child only via Capability/Runtime contract.
- Governor authority (T054); bounded recovery (T055) at parent scope.

### Out of scope
- Second control plane / broker, child execution primitive, policy engine.

## Deliverables
- `aios/multi_agent_autonomy/contracts.py` — Authority, DelegateRequest, DelegateResponse, DelegationDecision.
- `aios/multi_agent_autonomy/delegation.py` — AuthorityAttenuator, DelegationManager (anti-amplification, bounded limits, provenance).
- `aios/multi_agent_autonomy/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-059-01: Delegation creates sub-goal with clear scope + attenuated authority (not wholesale).
- AC-059-02: Child authority ⊆ Parent ∩ Scope ∩ Policy ∩ Budget (multi-dimensional).
- AC-059-03: Child authority == parent only if scope explicitly delegated.
- AC-059-04: Child authority > parent → BLOCK.
- AC-059-05: Child requests more authority → Governor/Policy → ALLOW/DENY/ASK_HUMAN (no self-escalation).
- AC-059-06: Grandchild delegation further attenuates.
- AC-059-07: Depth / child count / delegation budget / cumulative resource exceeded → BLOCK.
- AC-059-08: Parent accountable for aggregated outcome.
- AC-059-09: No subprocess/provider/filesystem import (architecture gate).
- AC-059-10: Regression M0–M8 PASS.

## Dependencies
- TASK-050 Goal Engine, TASK-054 Governor, TASK-055 Recovery, TASK-056 Durability, TASK-057 Memory, Orchestrator

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
