# AIOS — Operational Plan (Source of Truth)

> This file is the **operational** source of truth for AIOS development governance.
> The canonical task catalog is `docs/AIOS_Master_Task_Specification_M0-M26.md`
> (218 tasks, milestones **M0–M26**).
> A fresh session MUST read this file, `AGENTS.md`, and `aios/progress/README.md`
> before doing any task work — no chat memory required.

## 0. What AIOS is
AIOS = **AI Operating System**. Principles (from the master spec):
- **Runtime-First** · **Plugin-First** · **Offline-First** · **Harness-Verified** · **Coding-Plane**
- The deterministic control path is preferred over the LLM control path.
- Every claim of success must carry **evidence with provenance**; `UNKNOWN` is never `PASS`.

## 1. Quy tắc chung (General Rules — NON-NEGOTIABLE)
1. **TASK ID is immutable**; never reuse a number. Reserved IDs (e.g. TASK-076/077) stay placeholders.
2. **Dependency decides execution order**; **milestone decides product boundary**.
3. **Runtime is the control substrate**; Workers/Agents NEVER bypass Runtime, Capability, Permission, or Policy.
4. **LLM is NOT the default control plane**; the deterministic path goes first.
5. **Evidence must have provenance**; `UNKNOWN` is never promoted to `PASS`.
6. **A task closes ONLY after** spec → critique×2 → breakdown → review → implementation → test → evaluation → progress/log, per the master workflow.
7. **Every task must regression-test its prior dependencies.**

## 2. Task Folder Standard (per task)
Follow exactly `aios/progress/tasks/TASK-xxx/`:
`spec.md · critique-1.md · critique-2.md · tasks.md · review.md · implementation/ · test.md · evaluation.md`
Governance extensions (for Rules 5/7): `EVIDENCE.md` (provenance) · `REGRESSION.md` (dependency re-runs) · `STATUS.md` (lifecycle).

## 3. Definition of Done
```text
PLAN → SPEC → CRITIQUE×2 → BREAKDOWN → REVIEW
→ IMPLEMENT → TEST → EVALUATE → PROGRESS/LOG → COMMIT
```

## 4. Capability Chain (M0–M26)
```text
Governance → Runtime → Orchestrator → Desktop → Platform
→ Intelligence → Harness → Enterprise → Ecosystem → Autonomy
→ AIOS 1.0 → Deterministic Artifact → Compatibility
→ Harness Trust → Controlled Healing → Autonomous Harness
→ Independent Harness → Inference → Repository Context
→ Coder → Sandbox → Autonomous Coding Loop
→ Independent Verification → Adversarial Resilience
→ Quality Governance → Coding Evaluation → AIOS 2.0 Coding Edition
```

## 5. Coding Completion Contract
```text
AUTHORIZED · EXECUTED · VERIFIED · RESILIENT · GOVERNED · EVALUATED · CERTIFIED
```
A coding task is NOT complete merely because the agent stopped or the code runs.

## 6. How the General Rules are enforced (the "conditions" we prepared)
| Rule | Mechanism | Fail-closed |
|------|-----------|-------------|
| 1 — immutable IDs | `aios/scripts/parse_spec.py` generates `aios/progress/task-registry.json` and validates ID uniqueness. New tasks enter the master spec first, never hand-numbered. `TaskRegistry.create_task()` rejects duplicate IDs; no delete API — wrong tasks are `DEPRECATED`. | duplicate → `RegistryError` |
| 2 — dependency/milestone | `DependencyGraph.is_ready()` checks every dependency `status == PASS`; `detect_cycle()` blocks cyclic graphs; `parse_spec.py` derives milestone from `# Mx` headers → `task-index.md`; cross-milestone deps with later milestone → BLOCK. | unknown task / missing dep / cycle → BLOCK |
| 3 — Runtime substrate | `aios/governance/architecture/scan_source()` AST scan enforces `ARCH-001..004` (subprocess, os/pathlib/filesystem, provider, workflow↔engine, plus dynamic `__import__`/`importlib`). Violations in `implementation/*.py` → `ARCHITECTURE GATE FAIL → BLOCKED`. Extended repo-wide in TASK-016. | `import os` and `import subprocess` (any form) caught |
| 4 — deterministic-first | `DeterministicControlPath.route()` executes `Request → Normalizer → Rule Engine → … → Execution Plan` before LLM; LLM is fallback only when `can_decide==False` and its output MUST pass `validator`. Missing validator → `ControlPathError`. Gate records deterministic check. | no validator on fallback → error; `llm_calls==0` when rule decides |
| 5 — evidence provenance | `EvidenceStore.verify()` requires `evidence_id, run_id, parent_artifact, task, source, sha256:hash, status==PASS`; `hash` must match `sha256:[hex]{3,}`, `UNKNOWN` never PASS, evidence is task-scoped in `TaskGate`. Every task folder keeps `EVIDENCE.md` (source, sha256 hash, timestamp, actor) with provenance chain `Evidence → Run → Artifact → Task → Requirement`. | `n/a` / `UNKNOWN` / wrong-task evidence → FAIL |
| 6 — lifecycle gate | `TaskStateMachine` enforces `PLANNED→…→DONE` (12 states); `artifacts_present()` checks 11 artifacts non-empty; `gate_check.py` reads real `STATUS.md` state (not hardcoded DONE). Missing artifact or illegal transition → `BLOCKED`. | illegal transition / missing artifact / `STATUS.md != DONE` → BLOCKED |
| 7 — regression | `RegressionRunner.evaluate()` runs `graph.closure(task_id)` (transitive deps) via `run_test(t)`; exception → `False` (fail-closed). `TaskGate` computes it internally (no caller-supplied bool). Every task folder keeps `REGRESSION.md` referencing the dependency TASK-IDs it re-ran. | closure failure / exception → BLOCKED |

## 7. Starting a task (any agent / session)
1. Read `AGENTS.md`.
2. Copy `aios/progress/tasks/_TEMPLATE/` → `aios/progress/tasks/TASK-xxx/`.
3. Fill `spec.md`, then run critique×2, breakdown (`tasks.md`), review.
4. Implement under `implementation/`, record evidence in `EVIDENCE.md`.
5. Write `test.md` + `evaluation.md` + `REGRESSION.md`.
6. Run `python aios/scripts/gate_check.py TASK-xxx` → must pass before CLOSED.
7. Update `aios/progress/LOG.md` and commit.
