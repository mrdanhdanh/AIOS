# TASK-070 — Evaluation

## Acceptance criteria results
| AC | Result | Evidence |
|----|--------|----------|
| AC1 — external entry yêu cầu auth hợp lệ | PASS | `TestExternalAuth::test_missing_token_raises`, `test_unauthenticated_context_blocked`, `test_valid_token_authenticates` |
| AC2 — action không permission → BLOCK (fail-closed) | PASS | `TestPermissionFailClosed::test_no_grant_blocks`, `test_policy_deny_overrides_grant` |
| AC3 — secret không log plaintext / không leak | PASS | `TestSecretHandling::test_value_redacted_from_log`, `test_pattern_redacted`, `test_context_never_holds_secret_value` |
| AC4 — least-privilege enforced (vượt scope → BLOCK) | PASS | `TestLeastPrivilege::test_exceeded_scope_blocked`, `test_within_scope_allowed`, `test_wildcard_scope_allowed` |
| AC5 — privileged action ghi audit evidence (provenance) | PASS | `TestAuditTrail::test_privileged_action_audited`, `test_audit_uses_evidence_store` |
| AC6 — cùng context + action → cùng quyết định (deterministic) | PASS | `TestDeterminism::test_same_inputs_same_decision`, `test_deterministic_block` |
| AC7 — tích hợp Runtime + Governor (T054) + API | PASS | `TestIntegration::test_governor_scope_enforced`, `test_governor_scope_allows`, `test_api_bridge_builds_context` |

## Test Matrix
| Scenario | Expected | Result |
| -------- | -------- | ------ |
| external call không auth | BLOCK | PASS |
| action không permission | BLOCK (fail-closed) | PASS |
| secret trong log | redacted / blocked | PASS |
| vượt scope | BLOCK (least-privilege) | PASS |
| privileged action | audit evidence ghi | PASS |
| cùng context + action | cùng quyết định (deterministic) | PASS |

## Regression
- Dependency closure (T054, T017, T065): integration tests PASS; existing
  `aios/security/tests/test_security.py` (IsolationManager) không bị phá.
- Không vi phạm invariants (fail-closed, no secret leak, deterministic).
