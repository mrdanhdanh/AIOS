# TASK-162 — Replay & Flaky Detector

## Objective
Deterministic flakiness detection: a replay is flaky when repeated runs do not produce identical outcomes. Fail-closed: a run with no provenance is rejected; flaky -> INSUFFICIENT.

## Scope
- Package: `aios/verification/` (unknown/infra layer, deterministic-first, fail-closed, provenance-bearing).
- Module: `aios/verification/replay_flaky.py` — class `ReplayFlakyDetector`.
- No LLM, no I/O, no provider/filesystem imports (ARCH-001..004 N/A for unknown layer).

## Deliverables
- Implementation + contract/schema + deterministic tests + evidence + documentation.

## Acceptance Criteria
- ReplayRun/FlakyReport immutable with non-empty run_id (Rule 1).
- detect returns flaky = (len(set(outcomes)) > 1); PASS when stable.
- Empty run_id or empty outcomes raises VerificationError (fail-closed).
- Flaky -> status INSUFFICIENT (never promoted).
- report_id deterministic (sha256 of inputs).

## Dependencies
- T001 (Evidence/Rule 1/5/6), T078 (Integrity), T033 (Regression), T144 (Execution Evidence).
