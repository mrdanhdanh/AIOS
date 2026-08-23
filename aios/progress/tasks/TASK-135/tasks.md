# TASK-135 — Task Breakdown

1. Định nghĩa `ExecutionRequest` / `ExecutionResponse` schema (frozen dataclass, immutable `request_id`).
2. Định nghĩa `ExecutionStatus` enum (PENDING/RUNNING/SUCCESS/FAILED/BLOCKED).
3. Định nghĩa `CapabilityDispatcher` Protocol (dispatch -> ExecutionResponse).
4. Định nghĩa `ExecutionContract` với `sandbox_ref`/`policy_ref`/`artifact_ref`/`evidence_ref`.
5. Implement `validate_request` / `validate_response` fail-closed.
6. Implement `content_hash` + `provenance` (T001 Rule 5 / T078).
7. Viết tests (`test_contract.py`): 8 tests.
8. Chạy pytest + gate_check.
