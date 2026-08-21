# TASK-013 — Evaluation

## Verdict: PASS

Worker Plane meets spec in full. Four workers (General, Coder, Doctor, SystemDoctor) share a common contract with 10 mandatory fields, lifecycle state machine, capability-only access, permission boundary, structured result/evidence, routing and failure propagation. 161 new tests + 690 inherited = 851 total, 0 failed. Architecture Guard updated for worker layer (between orchestrator and runtime) with no violations.

## Strengths
- WorkerContract enforces all 10 mandatory fields with SemVer and capability validation; 4 worker types share same contract but specialize domain logic.
- Capability-only access via CapabilityRegistry — workers never import Tool/Runtime/Provider/filesystem/subprocess; verified by AST architecture tests.
- Permission boundary: worker cannot self-grant; must go through permission_checker → ALLOW/DENY; DENY→BLOCKED fail-closed.
- Lifecycle is state-machine controlled (REGISTERED→READY→ASSIGNED→RUNNING→COMPLETING→COMPLETED, failure path, terminal), thread-safe, distinct from Task lifecycle (worker reusable after task failure).
- Structured result with 5 statuses (SUCCEEDED/FAILED/BLOCKED/CANCELLED/PARTIAL), PARTIAL not auto-promoted; evidence with provenance chain Evidence→Run→Artifact→Task→Requirement, UNKNOWN never promoted to PASS.
- Router is capability-based (task_type + required_capabilities + health + policy), not name-only; deterministic (sorted by worker_id); fallback only when policy allows.
- Failure propagated to Orchestrator/FailureRecovery, not creating parallel control plane; worker reuse after COMPLETED/FAILED verified.
- Architecture Guard extended: LAYER_ORDER includes worker, ALLOWED_IMPORT_LAYERS restricts worker to capability/unknown, WORKER_FORBIDDEN covers subprocess/os/provider/filesystem/runtime internals.

## Risks / Limitations
- Worker persistence is in-memory with lifecycle state; no DB or distributed storage (deferred to M7).
- Worker execution is synchronous; no async/parallel worker pool (deferred to TASK-028 Parallel Scheduler).
- Capability invocation is mock (no real Tool execution); full Tool/Capability Router deferred to TASK-014.
- Worker health is set manually; no automatic health probing (deferred to TASK-021 Observability).

## Follow-up
- TASK-014 Tool + Capability Layer will provide full capability→tool resolution for ExecutionPlan nodes with health/priority/policy routing.
- TASK-016 Architecture Hardening will add cross-task architecture gate over worker layer.
- TASK-021 Observability will add automatic health probing and metrics for workers.

## Evidence
- `python -m pytest aios/worker -q` — 161 passed
- `python -m pytest aios -q` — 851 passed, 0 failed
- Architecture Guard: `python -m pytest aios/worker/tests/test_architecture.py -q` — 10 passed, 0 violations
- Worker layer classification: `classify_module("aios/worker/contract.py") == "worker"` verified
