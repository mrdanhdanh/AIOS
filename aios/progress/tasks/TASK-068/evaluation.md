# TASK-068 — Evaluation

## Acceptance criteria results
| AC | Result | Evidence |
|----|--------|----------|
| AC1 — mọi layer tôn trọng halt (fail-closed) | PASS | `test_manual_global_halt_stops_all_contexts_fail_closed`, `test_safety_source_halt_works` |
| AC2 — không phá state verified (durable) | PASS | `test_verified_state_survives_halt_and_drain` |
| AC3 — graceful drain + persist in-flight | PASS | `test_halt_mid_inflight_drains_and_persists` |
| AC4 — mọi halt ghi audit provenance | PASS | `test_halt_writes_auditable_evidence_with_provenance`, `test_controller_audit_uses_shared_evidence_store` |
| AC5 — deterministic (same signal+state) | PASS | `test_same_signal_is_deterministic_and_idempotent`, `test_two_controllers_same_state_same_result` |
| AC6 — tích hợp Governor (T054) | PASS | `test_governor_bridge_delegates_when_not_halted`, `test_governor_bridge_blocks_fail_closed_when_halted` |
| AC7 — không layer bypass halt | PASS | `test_layer_that_skips_halt_is_blocked_fail_closed`, `test_failing_drain_does_not_break_fail_closed` |
| AC8 — regression milestone trước | PASS | `regression.md` (không sửa dependency; chỉ chạy package tests) |

## Test Matrix
| Scenario | Expected | Test | Result |
| -------- | -------- | ---- | ------ |
| manual halt | mọi loop dừng (fail-closed) | `test_manual_global_halt_stops_all_contexts_fail_closed` | PASS |
| policy halt | dừng đúng scope | `test_policy_goal_scoped_halt_only_target` | PASS |
| halt giữa in-flight | drain + persist | `test_halt_mid_inflight_drains_and_persists` | PASS |
| layer cố skip halt | bị chặn (fail-closed) | `test_layer_that_skips_halt_is_blocked_fail_closed` | PASS |
| halt ghi audit | provenance đầy đủ | `test_halt_writes_auditable_evidence_with_provenance` | PASS |
| cùng halt signal + state | cùng hành vi | `test_same_signal_is_deterministic_and_idempotent` | PASS |

## Regression
- Dependency closure: T054 (governor) không bị sửa; T066/T067 chưa tồn tại →
  dùng fallback. Chỉ chạy `aios/kill_switch` tests → 23 passed, không break
  existing tests.
