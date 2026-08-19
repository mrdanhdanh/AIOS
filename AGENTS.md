# AGENTS.md — AIOS Development Agent Guide

You are an agent operating inside the AIOS repository. This file is the contract for HOW you work.
A new session MUST read `docs/PLAN.md`, this file, and `aios/progress/README.md` before any task work.

## The hard gate (Rule 6)
You may NOT mark a task CLOSED unless ALL of these exist and are non-empty:
- `spec.md`, `critique-1.md`, `critique-2.md`, `tasks.md`, `review.md`, `test.md`, `evaluation.md`
- `implementation/` with real code
- `EVIDENCE.md` (every PASS claim cites provenance)
- `REGRESSION.md` (dependency tasks re-run)
- `STATUS.md` with lifecycle state leading to CLOSED (only via `gate_check.py`)
Verify with: `python aios/scripts/gate_check.py TASK-xxx`

## General Rules (verbatim intent)
1. TASK IDs are immutable — never reuse. New work goes into the master spec first.
2. Respect dependency & milestone boundaries.
3. Never bypass Runtime / Capability / Permission / Policy.
4. Deterministic path first; LLM is fallback only.
5. Evidence needs provenance. `UNKNOWN` ≠ `PASS`. Fail-closed.
6. Full lifecycle required before CLOSE.
7. Regression-test prior dependencies; record in REGRESSION.md.

## Failure behavior
- If you cannot produce evidence, report `UNKNOWN` / `BLOCKED`. Do NOT claim PASS.
- If a dependency is unmet, do NOT start the dependent task.

## Roles (see `aios/agents/`)
- Orchestrator: `aios/agents/orchestrator.md`
- Spec-writer: `aios/agents/spec-writer.md`
- Critic (×2): `aios/agents/critic.md`
- Reviewer: `aios/agents/reviewer.md`

## Commands
- Regenerate registry: `python aios/scripts/parse_spec.py`
- Check a task gate: `python aios/scripts/gate_check.py TASK-xxx`
