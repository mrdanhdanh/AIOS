# AIOS — Agent Responsibilities & Boundaries (M0)

This file documents the agent roles and the architectural boundaries they must
respect. It is part of the self-verifying governance system (Rule 3:
Architecture Guard).

## 1. General architecture rule

Layering is enforced by `aios/governance/architecture`:

```
Agent -> Orchestrator -> Runtime -> Capability -> Tool
```

Imports must only go **downward**. Violations fail the architecture gate and
**BLOCK** the task.

## 2. Forbidden direct imports for agents (ARCH-001..003)

| Rule | Forbidden |
|------|-----------|
| ARCH-001 | `subprocess`, `os` (execution primitives) |
| ARCH-002 | provider adapters (`aios.core.providers`, `providers`, …) |
| ARCH-003 | filesystem adapters (`aios.runtime.filesystem`, `filesystem`, …) |

Agents obtain capabilities only through the interfaces passed into them by the
orchestrator / runtime — never by importing provider or tool internals.

## 3. Roles

### Orchestrator (`aios/agents/orchestrator.py`)
- Drives a task through its lifecycle via `TaskLifecycle`.
- Only marks a task `DONE` after the **Unified Task Gate** passes.
- Coordinates (does not implement) spec-writer, critic, reviewer.

### Spec-Writer (`aios/agents/spec_writer.py`)
- Renders `spec.md` from structured `SpecInput`.
- Pure text transformation; no I/O, no provider access.

### Critic (`aios/agents/critic.py`)
- Produces `critique-1.md` and `critique-2.md`.
- Pure analysis over a specification; flags missing sections.

### Reviewer (`aios/agents/reviewer.py`)
- Produces `review.md`.
- Verifies the mandatory pre-implementation artifacts are present.

## 4. Deterministic-first (Rule 4)

No agent may call an LLM as the default control path. The deterministic
pipeline (`aios/governance/deterministic`) decides whenever it can; the LLM is
only a fallback when the deterministic result is `INSUFFICIENT`, and its output
must pass a validator.

## 5. Evidence & provenance (Rule 5)

Any `PASS` must be backed by evidence with a complete provenance chain:
`Evidence -> Run -> Artifact -> Task -> Requirement`. `UNKNOWN` is never
promoted to `PASS`.
