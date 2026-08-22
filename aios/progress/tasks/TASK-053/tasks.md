# TASK-053 — Breakdown

## Steps
1. `aios/autonomous_loop/contracts.py` — AutonomousCycle, CycleStatus, Decision, StopCondition, CandidateLearning.
2. `aios/autonomous_loop/loop.py` — LoopController/AutonomousLoop: cycle orchestration, loop-level cost/failure accumulators, deterministic stop conditions.
3. `aios/autonomous_loop/tests/test_autonomous_loop.py` — 6 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-053-01..08 PASS, gate PASS, no regressions.
