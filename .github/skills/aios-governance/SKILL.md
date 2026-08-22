---
name: aios-governance
description: '**WORKFLOW SKILL** — Concise reference for AIOS project governance. Use when: starting or resuming an AIOS TASK; checking architecture layering (Agent→Orchestrator→Runtime→Capability→Tool); running governance gates; performing auto-commit (Quy tắc 8); verifying task lifecycle artifacts; or answering "what are the gates / rules / lifecycle states". Load this INSTEAD of re-reading docs/PLAN.md, aios/progress/LOG.md, aios/progress/PROGRESS.md, or docs/AIOS_Master_Task_Specification_M0-M26.md. DO NOT USE for: general Python coding questions.'
---

# AIOS Governance — Quick Reference

> Loaded on demand. For full detail, link (do not paste) `docs/PLAN.md`, `AGENTS.md`, `aios/progress/README.md`, `docs/detailtask/T00X.md`.

## Layering (ARCH-001..004, enforced by `aios/governance/architecture/guard.py`)
Imports only go **downward**: `Agent → Orchestrator → Runtime → Capability → Tool`.
- ARCH-001: no `subprocess`/`os` execution in agents
- ARCH-002: no provider adapters in agents
- ARCH-003: no filesystem adapters in agents
- ARCH-004: no upward / skip-layer imports (e.g. `tool → runtime`)
Agents get capabilities only via injected interfaces — never import provider/tool internals.

## 7 Gates → Unified Task Gate (logical AND, fail-closed)
`UnifiedTaskGate` passes only when ALL pass; any exception → FAIL; `DONE` only on `PASS`.
1. **Registry** — task IDs unique/immutable/never-reused; `deprecate()` is soft-delete
2. **Dependency** — DAG via `governance/dependency/graph.py`; `is_ready()`, `detect_cycle()`
3. **Architecture** — §layering above
4. **Deterministic** — `governance/deterministic/pipeline.py`; `KNOWN_INTENTS={status,health,help,list tasks}` → `SUFFICIENT` (no LLM); else `INSUFFICIENT` → optional `llm_fallback`
5. **Evidence** — `Evidence → Run → Artifact → Task → Requirement`; `content_hash=sha256`; `UNKNOWN` never promoted to `PASS`
6. **Lifecycle** — 12 states `PLANNED→…→DONE`; `STATE_ARTIFACTS` (spec.md, critique-1/2.md, tasks.md, review.md, implementation/, test.md, evaluation.md, regression.md); `can_close()` requires `READY_TO_CLOSE` + `missing_for_done()==[]`
7. **Regression** — `governance/regression/runner.py`; first `FAIL` → `blocked=True`

## Quy tắc 8 — Auto-COMMIT (mandatory)
Every scheduled TASK reaching `DONE` (Unified Gate `PASS`) must `COMMIT` source **in the same session** — never leave working tree dirty into the next task.
- Message: `TASK-xxx: <title> — DONE`
- Also update `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` + related evidence.

## Local CI gate before push / claim DONE (mandatory)
Always run `aiagent ci check` (or `python aios/governance/cli/gate_check.py --task TASK-00X`, default `--ci` on, scope=full) before push or declaring DONE. Never push on local CI FAIL (fail-closed). Catches e.g. `ModuleNotFoundError: fastapi` (missing `api` extra) early.

## Conventions
- Python ≥3.11, `pyyaml` only runtime dep. `pip install -e ".[dev]"` before `pytest`; add `,api` for TASK-017+ (FastAPI).
- Agents: pure, I/O-free. All I/O, provider, filesystem via Runtime.
- Naming: `TASK-xxx` immutable, never reused.
- Diagnose before retry: on fail, run `gate_check.py --task TASK-00X` + `pytest aios -q`, report `Violation(rule,module,line)` or test failure — no blind "Try Again".
- PowerShell contract (Windows): no bash-isms (`head`, `&&`, `grep`); use `Select-Object`, `Select-String`, `;`.
- Workspace path: relative `${workspaceFolder}` (`d:\AIOS` / `aios/...`); never hardcode legacy `OneDrive\Desktop\AIAGENT`.
- Communicate in **Vietnamese**; commit messages / code comments in English.
- Short approval ("có"/"duyệt"/"ok") = proceed to next step, no re-confirm.
- Self-drive scheduled TASK chains; STOP after the same error repeats — report root cause, wait for user.
