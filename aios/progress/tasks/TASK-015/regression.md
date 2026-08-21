# TASK-015 — Regression

## Dependency closure
`{ TASK-014, M1 (TASK-003..009,011), TASK-010/012/013 }` — all DONE.

## Full suite before/after
- Before T015: 1014 tests green (TASK-014).
- After T015: 1181 (1014 + 167 skill). After T016: **1257** full-suite green.

## Architecture gate
- `aios/governance/architecture` gate: PASS (fail-closed).
- Skill layer added to `guard.py` (`LAYER_ORDER`/`SKILL_FORBIDDEN`); rule
  ARCH-H-001 (INV-010) enforces no Core/Runtime bypass.
- No new import-boundary or reverse-dependency violations introduced.

## Kernel wiring regression
`RuntimeKernel` instantiates SkillManager/SandboxPool/SkillRegistry without
circular-import errors; `health()` extended with `skills_registered` and
`sandbox_pool_size`.
