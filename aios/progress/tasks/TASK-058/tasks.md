# TASK-058 — Breakdown

## Steps
1. `aios/autonomous_experimentation/contracts.py` — Experiment, ExperimentStatus, MetricSpec, PromotionDecision.
2. `aios/autonomous_experimentation/controller.py` — ExperimentController: propose (validate), authorize (governor), run (harness), evaluate (promotion gate).
3. `aios/autonomous_experimentation/tests/test_autonomous_experimentation.py` — 9 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-058-01..12 PASS, gate PASS, no regressions.
