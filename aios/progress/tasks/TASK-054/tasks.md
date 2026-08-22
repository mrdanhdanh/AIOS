# TASK-054 — Breakdown

## Steps
1. `aios/autonomy_governor/contracts.py` — AutonomyPolicy/Mode/Action/Risk/Decision/Budget/ApprovalRequest.
2. `aios/autonomy_governor/governor.py` — AutonomyGovernor: classify_action, score_risk, check_scope, check_budget, decide (fail-closed), request_approval.
3. `aios/autonomy_governor/tests/test_autonomy_governor.py` — 11 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-054-01..09 PASS, gate PASS, no regressions.
