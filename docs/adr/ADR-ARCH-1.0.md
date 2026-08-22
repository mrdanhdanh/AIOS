# ADR-ARCH-1.0 — AIOS Architecture Baseline 1.0 Freeze

- **Status:** Accepted (Frozen)
- **Date:** 2026-08-22
- **Task:** TASK-063 (M10 — Architecture 1.0)
- **Supersedes:** none (initial freeze)
- **Superseded by:** none

## 1. Context

AIOS has accumulated layered modules (`api`, `agent`, `orchestrator`, `worker`,
`runtime`, `skill`, `capability`, `tool`) enforced by the Architecture Guard
(`aios/governance/architecture/guard.py`). TASK-063 freezes this layering as the
**official 1.0 baseline** so that every subsequent task (notably T064 Contract
Freeze) and the CI gate share one stable, codified reference. This ADR is the
human-readable counterpart to the codified constants in
`aios/governance/architecture/baseline.py`.

## 2. Decision

### 2.1 Frozen layer order

Imports must only go **downward** (caller → callee). The canonical order is:

```
api > agent > orchestrator > worker > runtime > skill > capability > tool
```

Represented in code as:

```python
LAYER_ORDER = ["api", "agent", "orchestrator", "worker",
               "runtime", "skill", "capability", "tool"]
```

`core`, `governance`, `harness`, `progress` are **infra/meta** layers and map to
`unknown` so they never trigger ARCH-004 false positives on stdlib/infra imports.
`kernel`/`workflow` map to `runtime`.

### 2.2 Codified rules (ARCH-001..004)

| Rule | Forbids | Applies to |
|------|---------|------------|
| ARCH-001 | direct import of execution primitives (`subprocess`, `os`) | agent, worker, skill |
| ARCH-002 | direct import of provider adapters (`aios.core.providers`, `aios.runtime.providers`, `providers`) | agent, worker, skill |
| ARCH-003 | direct import of filesystem adapters (`aios.runtime.filesystem`, `aios.runtime.fs_adapter`, `filesystem`) | agent, worker, skill |
| ARCH-004 | upward / skip-layer import (e.g. `tool` → `runtime`) | all layers |

### 2.3 Single source of truth

The frozen constants live **only** in `aios/governance/architecture/guard.py`.
`aios/governance/architecture/baseline.py` re-exports them (copies) and pins
`ARCHITECTURE_VERSION = "1.0"`. No other module may redefine the layer order or
rules.

## 3. Freeze safety principles

- **No silent change** — any change to the layer contract or ARCH rules requires
  a new ADR and an `ARCHITECTURE_VERSION` bump. Editing `LAYER_ORDER`/`ARCH_RULES`
  without an ADR is a governance violation.
- **Fail-closed** — a parse error (`ArchitectureError`) or any `Violation` makes
  the gate `FAIL` and BLOCKS the task. The guard never downgrades a violation to a
  warning.
- **Deterministic** — for a fixed source tree and a fixed guard version, the scan
  result is identical (pure AST analysis, no network/clock/randomness).
- **No parallel architecture** — exactly one layer order exists. A second parallel
  layering must never be introduced.

## 4. Consequences

- The Architecture Guard runs in CI (local + remote) before every `DONE`.
- T064 and all post-1.0 tasks reference this baseline.
- Changing the contract is now an explicit, reviewable, versioned event.

## 5. Validation

Covered by `aios/governance/architecture/tests/` (test matrix in TASK-063
`evaluation.md`): agent→subprocess (ARCH-001), agent→provider (ARCH-002),
agent→filesystem (ARCH-003), tool→runtime (ARCH-004), correct downward (PASS),
parse error (BLOCK), deterministic (same result).
