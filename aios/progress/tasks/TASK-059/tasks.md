# TASK-059 — Breakdown

## Steps
1. `aios/multi_agent_autonomy/contracts.py` — Authority, DelegateRequest, DelegateResponse, DelegationDecision.
2. `aios/multi_agent_autonomy/delegation.py` — AuthorityAttenuator, DelegationManager (attenuate, anti-amplification, bounded limits, provenance).
3. `aios/multi_agent_autonomy/tests/test_multi_agent_autonomy.py` — 8 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-059-01..10 PASS, gate PASS, no regressions.
