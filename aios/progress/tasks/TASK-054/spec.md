# TASK-054 — Autonomy Governor

## Objective
Build the autonomy governance layer that gates every autonomous action before execution: scope / risk / policy / permission / resource-budget / action-limit / approval checks. The Governor does NOT replace the Policy Engine — it consumes existing policy/permission/runtime contracts. Fail-closed: uncertainty → BLOCK.

## Scope
### In scope
- `AutonomyPolicy` (mode: disabled/supervised/bounded/autonomous; limits; per-action rules; approval rules).
- `AutonomyAction` classification: READ/WRITE/EXECUTE/NETWORK/CREDENTIAL/INSTALL/MODIFY_SYSTEM/DESTRUCTIVE/POLICY_ESCALATION.
- `AutonomyRisk` scoring (LOW/MEDIUM/HIGH/CRITICAL) = action + resource + target + privilege + reversibility + cumulative risk (deterministic, no LLM).
- `AutonomyBudget` tracking (steps/tool_calls/runtime/tokens/cost/retries/cumulative_risk); over budget → LIMIT_REACHED → BLOCK.
- Scope boundary: goal allowed scope (workspace/files/capabilities/tools/network/resources/time); out-of-scope → DENY/ASK.
- `ApprovalRequest` (goal/action/target/reason/risk/requested_permissions/resource_estimate/expected_side_effect/rollback_strategy/evidence) with expiry, non-reusable.
- `AutonomyDecision` (ALLOW/BLOCK/ASK) with fail-closed default.

### Out of scope
- Policy Engine itself, Permission Service internals, Recovery (T055), Evaluation (T060).

## Deliverables
- `aios/autonomy_governor/contracts.py` — AutonomyPolicy/Mode/Action/Risk/Decision/Budget/ApprovalRequest.
- `aios/autonomy_governor/governor.py` — AutonomyGovernor (classify/score/check/decide/request_approval).
- `aios/autonomy_governor/tests/` — unit/contract/integration/architecture tests.

## Acceptance Criteria
- AC-054-01: Policy modes + per-action rules modeled.
- AC-054-02: Action classification covers all 9 action types.
- AC-054-03: Deterministic risk scoring → level.
- AC-054-04: Budget tracking; over budget → BLOCK.
- AC-054-05: Scope violation → BLOCK/ASK (no silent expansion).
- AC-054-06: Approval request with expiry, non-reusable.
- AC-054-07: Fail-closed — unknown/uncertain → BLOCK.
- AC-054-08: No subprocess/provider/filesystem import (architecture gate).
- AC-054-09: Regression M0–M8 PASS.

## Dependencies
- TASK-053 Autonomous Loop

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
