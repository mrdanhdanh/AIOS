# TASK-226 — Deterministic Auto-Stop / RetryGuard

> **Trạng thái thực tế (2026-08-25):** PLANNED — implementation + tests written, awaiting governance gate run (terminal disabled at build time). See `docs/AIOS_Master_Task_Specification_M0-M26.md` TASK-226 block.

## Problem
Session store shows **165 retry-loop occurrences** ("thử lại"/"Try Again"/"tiếp tục") across 637 turns (~26%), consistent with `/chronicle improve` in `AGENTS.md §12`. The auto-stop rule exists only as prose; nothing in code halts repeated identical failures. Agents can loop "Try Again" indefinitely.

## Objective
Codify the auto-stop rule as a deterministic, fail-closed runtime capability: `RetryGuard` detects when the same failure signature repeats >= threshold and halts with a root-cause report.

## Acceptance Criteria
1. `RetryGuard.observe()` returns True at/after `threshold` identical failures.
2. Distinct signatures are tracked independently (no false stop).
3. `report()` returns a root-cause message with signature + count + last message.
4. Invalid threshold / empty signature raise `ValueError` (fail-closed).
5. Architecture gate 0 violations (runtime layer, no agent imports).
6. Unit tests pass; full suite no regression.
7. Wired conceptually into orchestrator loop via capability injection (not direct import).
