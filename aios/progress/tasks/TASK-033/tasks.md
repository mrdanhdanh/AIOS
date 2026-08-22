# TASK-033 — Breakdown

## Steps
1. Create `aios/harness/benchmark.py` — BaselineManager (set/get/has_baseline), BenchmarkRun, MetricComparison, ComparisonResult
2. Implement RegressionDetector: compare baseline vs current per metric with threshold, return IMPROVED/REGRESSED/STABLE/INCONCLUSIVE
3. Implement ReleaseGate: check comparisons, any REGRESSED → not passed
4. Create `aios/harness/tests/test_benchmark.py` — 6 tests (baseline manager, no baseline, regression detection, no regression, gate pass, gate fail)
5. Run architecture guard — verify no Harness → Runtime implementation
6. Run full suite — 1749/1749 PASS (6 new), no regressions

## Dependencies
- TASK-032 Evaluation Harness

## Exit Criteria
- All AC-033-01..10 PASS, gate PASS, no regressions
