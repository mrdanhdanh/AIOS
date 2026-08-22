# TASK-043 — Public AIOS SDK

## Objective
Build the Public AIOS SDK as the official developer-facing layer (Python/TS) that exposes stable, versioned, contract-first APIs for Agent, Tool, Capability, Skill, Workflow, Prompt, Execution, Artifact, and Event. SDK uses canonical contracts shared with REST API and Extension, with offline-capable Mock/Local Runtime. No direct Runtime/Orchestrator implementation access, no Policy/Permission bypass.

## Scope
### In scope
- Python SDK: declarative decorators (@aios.tool, @aios.agent, @aios.workflow), builders, discovery, execution, artifacts, events
- TypeScript SDK: shared client for Dashboard, VS Code Extension, external integrations
- Contract synchronization: Canonical Contracts → Python SDK, TypeScript SDK, REST API, Extension (no separate SDK schema)
- Versioning: SDK version, contract version, schema version, compatibility metadata, deprecation policy
- Public API boundary: SDK can create/register/discover/submit execution/read state/get artifact/subscribe event/query health; cannot access Runtime implementation, bypass Policy/Permission, call Tool directly, access DB
- Error model: ValidationError, AuthenticationError, AuthorizationError, PolicyDeniedError, etc. with provenance
- Offline-first with Mock/Local Runtime

### Out of scope
- Plugin Runtime lifecycle (TASK-044)
- Extension Contracts (TASK-045)
- Creating a parallel control plane

## Deliverables
- `aios/sdk/contracts.py` — SDKConfig, SDKResponse, ErrorCode, SDKError
- `aios/sdk/client.py` — AIOSClient (health, execute, list_resources, config)
- `aios/sdk/tests/` — SDK tests

## Acceptance Criteria
- AC-043-01: Developer can use AIOS via SDK without importing internal Runtime/Orchestrator
- AC-043-02: SDK uses canonical contracts; mismatch rejected
- AC-043-03: Python SDK can define/register/execute component via public SDK
- AC-043-04: TypeScript SDK can connect and perform basic public operations
- AC-043-05: Policy deny → PolicyDeniedError, no bypass
- AC-043-06: Permission-sensitive ops go through permission boundary
- AC-043-07: Mock/local execution works without external LLM/provider
- AC-043-08: Incompatible contract/version detected deterministically before execution
- AC-043-09: Internal errors not leaked as uncontrolled public API
- AC-043-10: Regression M0–M7 PASS, no invariant violation

## Dependencies
- TASK-042 — Enterprise Operations + Dashboard

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
