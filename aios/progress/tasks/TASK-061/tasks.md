# TASK-061 — Breakdown

## Steps
1. `aios/stuck_detection/contracts.py` — StuckSignal, StuckKind, StuckSeverity, StuckPolicy.
2. `aios/stuck_detection/detector.py` — StuckDetector (monitor + oscillation/plateau/resource-burn), StuckGate.
3. `aios/stuck_detection/tests/test_stuck_detection.py` — 11 tests.
4. Run architecture guard — no subprocess/provider/filesystem import.
5. Run full suite — no regressions.

## Exit Criteria
- All AC-061-01..13 PASS, gate PASS, no regressions.
