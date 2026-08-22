# TASK-061 — Evaluation

| AC | File | Status | Evidence |
|----|------|--------|----------|
| AC-061-01 | detector.py | PASS | test_every_iteration_monitored |
| AC-061-02 | detector.py | PASS | 3 tiers |
| AC-061-03 | detector.py | PASS | test_oscillation_detected_from_trajectory_hash |
| AC-061-04 | detector.py | PASS | test_plateau_detected |
| AC-061-05 | detector.py | PASS | test_resource_burn_detected |
| AC-061-06 | contracts.py | PASS | test_low_confidence_escalates_fail_closed |
| AC-061-07 | detector.py | PASS | signal never auto-promotes |
| AC-061-08 | detector.py | PASS | test_stuck_gate_blocks_on_budget |
| AC-061-09 | detector.py | PASS | signals carry evidence_ref |
| AC-061-10 | detector.py | PASS | test_deterministic_same_trajectory_same_verdict |
| AC-061-11 | detector.py | PASS | integrates with loop/eval |
| AC-061-12 | (architecture) | PASS | no second control plane |
| AC-061-13 | (regression) | PASS | full suite green |

## Verdict
DONE — Unified Task Gate PASS.
