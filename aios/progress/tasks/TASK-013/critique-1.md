# TASK-013 — Critique 1 (Spec Review)

## Strengths
- Spec scopes Worker Plane correctly as business execution layer above Orchestrator: 4 workers (General/Coder/Doctor/SystemDoctor) with shared contract, lifecycle, capability access, result/evidence.
- Deliverables pin exact files (`contract.py`, `lifecycle.py`, `registry.py`, `router.py`, `execution.py`, `workers.py`) with contracts rõ, thread-safe, fail-closed, deterministic.
- AC-013-01..11 mirror T013.md test scenarios (contract, capability-only, runtime/permission boundary, lifecycle, result/evidence, routing, failure, architecture, regression) và gate requirements.
- Out-of-scope explicitly defers Tool Router (TASK-014), Plugin/Skill (TASK-015), Architecture Hardening (TASK-016), API/UI (M3).

## Risks / Gaps
- Worker Contract must define all 10 fields (worker_id, worker_type, version, capabilities, input_schema, output_schema, lifecycle, execution_context, policy_context, evidence_contract) — need validation for each.
- Capability-only access must be enforced via Architecture Guard (worker layer only imports capability/unknown) — need AST tests for Worker→Tool/subprocess/Provider/filesystem.
- Permission boundary: worker must not self-grant permission; must go through PolicyEngine/PermissionBroker → ALLOW/DENY — need explicit test for DENY→BLOCKED.
- Lifecycle must be distinct from Task lifecycle (Worker READY ≠ Task SUCCEEDED) — need test for worker reuse after task failure.
- Evidence provenance chain Evidence→Run→Artifact→Task→Requirement must be complete; UNKNOWN never promoted to PASS — need evidence store integration test.

## Required revisions
- [x] Lock WorkerContract with 10 mandatory fields + SemVer validation + capability allowlist.
- [x] Define WorkerStatus lifecycle REGISTERED→READY→ASSIGNED→RUNNING→COMPLETING→COMPLETED with failure path and terminal states.
- [x] Implement WorkerRegistry with health tracking (REGISTERED/READY/BUSY/DEGRADED/UNAVAILABLE) and thread-safe RLock.
- [x] Implement WorkerRouter with capability-based routing (task_type + required_capabilities + health + policy), not name-only.
- [x] Add BaseWorker with capability-only access, permission boundary, execution_context isolation, structured result, evidence.

## Decision
- APPROVE with required revisions addressed — proceed to critique-2.
