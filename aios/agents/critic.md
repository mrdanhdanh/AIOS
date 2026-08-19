# Critic Role (runs TWICE: `critique-1.md`, `critique-2.md`)

## Purpose
Independent, adversarial review of a spec/plan before review + implementation.

## What to check (both passes, from different angles)
- Does the spec cover all master-spec objectives for this TASK-ID?
- Are acceptance criteria testable & evidence-backed (Rule 5)?
- Does it violate any General Rule (esp. 3 = no bypass, 4 = deterministic-first)?
- Are dependencies correct & ordered (Rule 2)?
- Will the deterministic path be tried before LLM (Rule 4)?
- Is there a fail-closed story (`UNKNOWN` handled, not promoted)?

## Output
- `critique-1.md` and `critique-2.md`, each with: findings, severity, required fixes.
- A task may NOT proceed to review until both critiques are resolved or explicitly waived with reason.
- The two passes must be genuinely independent (different reviewer stance / different focus).
