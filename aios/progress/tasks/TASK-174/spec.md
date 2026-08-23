# TASK-174 — Collusion Detector + Resilience Score + Attack Corpus Regression

## Objective
Integration capability aggregating attacker results: detect collusion (>=2 breaches), compute resilience score, and verify attack corpus has not regressed. Deterministic, fail-closed.

## Scope
- Package: `aios/adversarial/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/adversarial/collusion_detector.py` — class `CollusionDetector`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- CollusionReport/ResilienceReport/AttackCorpusRegression immutable with non-empty ids (Rule 1).
- detect: collusion when breaches >= 2 -> INSUFFICIENT; else PASS.
- score_resilience: score = blocked/total; PASS at >= 0.8 threshold.
- check_corpus_regression: regressed when current < baseline -> INSUFFICIENT.
- Empty attack_id or non-negative baseline/current enforced (fail-closed); ids deterministic.

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T164 (Verification Harness), T033 (Regression).
