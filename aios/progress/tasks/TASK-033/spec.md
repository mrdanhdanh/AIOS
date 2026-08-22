# TASK-033 — Benchmark + Regression Gate

## Objective
Build the Benchmark and Regression Gate that compares candidate vs baseline across Quality, Cost, Latency, Tokens, Failure Rate, and Policy Violations using TASK-032 Evaluation results and TASK-030 Evidence. Transforms benchmark comparison into a controlled release decision (PASS/WARNING/FAIL) with evidence and provenance.

## Scope
### In scope
- Benchmark contracts: BenchmarkRun, BenchmarkBaseline, BenchmarkCandidate, BenchmarkMetric, BenchmarkComparison, RegressionFinding, BenchmarkVerdict, BenchmarkReport
- Benchmark Runner: load suite → resolve baseline → execute/evaluate → collect metrics → aggregate → compare → detect regression → evaluate gate → persist evidence → report
- Metric model with direction (higher-is-better / lower-is-better), threshold, provenance
- Baseline management (version, commit, config, model/provider, prompt versions, suite version, environment)
- Metric Comparator and Regression Detector (NO_REGRESSION / REGRESSION / WARNING / INCONCLUSIVE)
- Gate Evaluator (PASS / WARNING / FAIL / INCONCLUSIVE) with hard gates (policy violation, critical scenario failure, missing evidence)
- Scenario-level benchmark (critical scenario failure → overall FAIL even if average improves)
- Evidence Package and Benchmark Report

### Out of scope
- Replacing Evaluation/Test/Verification Harness
- Creating a parallel evaluation engine or new Runtime
- Enterprise analytics (M7+)

## Deliverables
- `aios/harness/benchmark.py` — BaselineManager, BenchmarkRun, MetricComparison, RegressionDetector, ReleaseGate, ComparisonResult
- `aios/harness/tests/test_benchmark.py` — benchmark and regression gate tests

## Acceptance Criteria
- AC-033-01: Benchmark has clear baseline identity (version, commit, config, model, suite version, environment)
- AC-033-02: No baseline → INCONCLUSIVE (not PASS)
- AC-033-03: Metric comparison respects direction and threshold
- AC-033-04: Regression detected per metric with delta and severity
- AC-033-05: Hard regression (policy violation, critical scenario) → FAIL
- AC-033-06: Gate returns PASS/WARNING/FAIL/INCONCLUSIVE correctly
- AC-033-07: Scenario-level regression not hidden by average
- AC-033-08: Evidence Package created and traceable (Benchmark → Evaluation → Harness → Execution → Scenario)
- AC-033-09: Reproducibility metadata preserved
- AC-033-10: Regression M0–M5 + M6 (029-032) PASS

## Dependencies
- TASK-032 — Evaluation Harness + Metrics

## Governance references
- Rule 1..7 satisfied via `aios/governance/*`.
- INV-017..021 enforced.
