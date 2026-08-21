# TASK-013 — Test Report

## Suites

| Suite | File | Cases | Result |
|-------|------|-------|--------|
| worker contract | `aios/worker/tests/test_contract.py` | 27 | PASS |
| worker lifecycle | `aios/worker/tests/test_lifecycle.py` | 22 | PASS |
| worker registry | `aios/worker/tests/test_registry.py` | 20 | PASS |
| worker router | `aios/worker/tests/test_router.py` | 18 | PASS |
| worker execution | `aios/worker/tests/test_execution.py` | 22 | PASS |
| concrete workers | `aios/worker/tests/test_workers.py` | 28 | PASS |
| worker architecture | `aios/worker/tests/test_architecture.py` | 10 | PASS |
| worker integration | `aios/worker/tests/test_integration.py` | 14 | PASS |
| full harness | `python -m pytest aios -q` | 851 | PASS |

## Coverage

- **WorkerContract**: 10 mandatory fields (worker_id, worker_type, version, capabilities, input_schema, output_schema, lifecycle, execution_context, policy_context, evidence_contract), SemVer validation, capability allowlist, 4 worker types, to_dict/from_dict roundtrip, invalid id/version/capability/type reject.
- **WorkerRequest**: task_id/goal_id/objective/constraints/allowed_capabilities/context/policy_context, validation, to_dict/from_dict, goal_id optional.
- **WorkerContext**: run_id/task_id/worker_id/capability_scope/permissions, can_use_capability, isolation (scope not self-expandable), to_dict/from_dict.
- **WorkerResult**: SUCCEEDED/FAILED/BLOCKED/CANCELLED/PARTIAL, PARTIAL not auto-promoted, is_success/is_failure, to_dict/from_dict, invalid status reject.
- **WorkerEvidence**: evidence_id/task_id/run_id/producer/type/source/content_hash, provenance chain Evidence→Run→Artifact→Task→Requirement, UNKNOWN not promoted to PASS, is_admissible, to_dict/from_dict, missing field reject, compute_hash deterministic.
- **WorkerLifecycle**: REGISTERED→READY→ASSIGNED→RUNNING→COMPLETING→COMPLETED, failure RUNNING→FAILED→RECOVERING→READY/FAILED, terminal COMPLETED/CANCELLED, health REGISTERED/READY/BUSY/DEGRADED/UNAVAILABLE, valid transitions, invalid reject, terminal no further, can_transition, health tracking, set_health, worker reuse after failure, list/clear/remove, to_dict, thread-safety, string transitions.
- **WorkerRegistry**: register/get/list/remove, health tracking, duplicate/unknown reject, non-contract reject, list sorted/by_type/by_health, set_health, is_available, available_workers, set_status, clear, to_dict, thread-safety, 4 workers registered.
- **WorkerRouter**: route general/coding/diagnosis/system_diagnosis, capability-based (not name-only), unhealthy/degraded skipped, preferred worker, no matching capability fail, policy-gated, empty capabilities, task_type aliases, can_route, history, validation, deterministic (sorted by worker_id).
- **WorkerExecution**: capability-only access (contract + scope checks), permission boundary (checker delegate, fail-closed, cannot self-grant), execute succeeded/with context, scope not in contract → FAILED, failure propagated, permission denied → BLOCKED, lifecycle transitions, reuse after COMPLETED/FAILED, invalid request/context reject, create_evidence, health, no runtime/orchestrator/subprocess imports.
- **Concrete Workers**: GeneralWorker (research/summarize/transform/inspect/coordinate), CoderWorker (code.read/write/test.run/analyze/refactor, no subprocess/open/requests), DoctorWorker (diagnose task failure, 5 categories, only diagnoses), SystemDoctorWorker (runtime health, 3 statuses, only proposes), all 10 fields, distinct types, evidence, no direct Tool imports.
- **Architecture**: worker does not import runtime/orchestrator/agents/tool/subprocess/os/providers, only capability/unknown, guard classification, forbidden imports detected, no direct Tool instantiation.
- **Integration**: full routing+execution, doctor diagnoses coder failure, system doctor runtime diagnosis, failure propagated not control plane, worker reuse after failure, evidence provenance, capability isolation, routing with health/policy, all 4 workers execute.
- `python -m pytest aios -q` — 851 passed, 0 failed.

## AC mapping

| AC | Cases | Result |
|----|-------|--------|
| AC-013-01 contract | test_contract::test_worker_contract_* + test_workers::TestAllWorkersShareContract | PASS |
| AC-013-02 capability-only | test_execution::TestCapabilityOnlyAccess + test_architecture::test_worker_only_imports_allowed_layers | PASS |
| AC-013-03 runtime boundary | test_execution::test_worker_does_not_import_runtime + test_architecture::test_worker_does_not_import_runtime | PASS |
| AC-013-04 permission boundary | test_execution::TestPermissionBoundary + test_workers::test_execute_with_limited_scope | PASS |
| AC-013-05 lifecycle | test_lifecycle (22) + test_registry::test_set_status | PASS |
| AC-013-06 result | test_contract::test_worker_result_* + test_execution::TestWorkerExecution | PASS |
| AC-013-07 evidence | test_contract::test_worker_evidence_* + test_integration::test_evidence_provenance_chain | PASS |
| AC-013-08 routing | test_router (18) + test_integration::TestWorkerRoutingIntegration | PASS |
| AC-013-09 failure | test_execution::test_execute_failure_propagated + test_integration::test_worker_failure_propagated_not_control_plane | PASS |
| AC-013-10 architecture | test_architecture (10) — guard PASS, no Worker→Tool/subprocess/Provider/filesystem | PASS |
| AC-013-11 regression | full harness 851 | PASS |
