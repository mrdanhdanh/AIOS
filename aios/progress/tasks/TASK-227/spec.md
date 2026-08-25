# TASK-227 — StubGuard: reject null-stub / SKIPPED pipeline steps

> **Trạng thái thực tế (2026-08-25):** PLANNED — implementation + tests written, awaiting governance gate run. Self-Improver TASK-225 proposed this from 44 skipped-stub signals (after retry-loop was fixed in TASK-226).

## Problem
Session store shows **44 skipped-stub / null-stub occurrences** ("SKIPPED", "null-stub", "_Null"). AGENTS.md §12 forbids null-stub / SKIPPED steps, but nothing in code enforces it — a pipeline step can silently report SKIPPED and the task is wrongly claimed successful.

## Objective
Codify the anti-stub rule as a deterministic, fail-closed runtime capability: `StubGuard` validates every pipeline step status and rejects SKIPPED/null-stub steps with a report.

## Acceptance Criteria
1. `StubGuard.is_skip()` returns True for SKIPPED/null/stub/_Null/unknown statuses.
2. `violations()` lists offending steps; `is_clean()` True only when none.
3. `report()` returns a human-readable list of violations.
4. Empty step_id/status raise `ValueError` (fail-closed).
5. Architecture gate 0 violations (runtime layer, no agent imports).
6. Unit tests pass; full suite no regression.
