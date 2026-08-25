# Superpowers -> AIOS Integration

Source methodology: [obra/superpowers](https://github.com/obra/superpowers) (MIT).
Integrated as AIOS skills under `skills/superpowers/` plus a deterministic router
`aios/skill/superpowers_router.py`.

## Philosophy (Superpowers) -> AIOS component

| Superpowers principle | AIOS equivalent |
|-----------------------|-----------------|
| Test-Driven Development (write tests first) | `python -m pytest aios -q`, `fail_under: 80` (pyproject.toml) |
| Systematic over ad-hoc (process over guessing) | Deterministic pipeline (Rule 4), `governance/deterministic/pipeline.py` |
| Complexity reduction (simplicity first) | ArchitectureGuard (Rule 3), `LAYER_ORDER` enforcement |
| Evidence over claims (verify before success) | EvidenceStore + provenance (Rule 5), `UnifiedTaskGate` |
| Skill-before-action (using-superpowers) | `superpowers_router.route()` + deterministic-first (Rule 4) |

## Skills delivered

Twelve AIOS-adapted skills, each with `SKILL.md`, `manifest.json`,
`catalog/skill-<id>.json`, `prompts/instructions.md`:

1. `using-superpowers` - meta-rule: invoke skill before any action.
2. `brainstorming` - Spike/Bounded/Architectural paths + approval HARD-GATE.
3. `systematic-debugging` - 4 phases, iron law: root cause before fix.
4. `test-driven-development` - RED/GREEN/REFACTOR, no code before failing test.
5. `verification-before-completion` - no claim without fresh evidence.
6. `writing-plans` - bite-sized TDD tasks (maps to `aios-plan` / `plan.yaml`).
7. `executing-plans` - load, review, execute, verify, finish.
8. `subagent-driven-development` - fresh subagent per task + ledger of rulings.
9. `requesting-code-review` - review package + fresh reviewer.
10. `receiving-code-review` - process findings at root, re-verify.
11. `using-git-worktrees` - isolated workspace (maps to `work/YYYYMMDD-slug/`).
12. `finishing-a-development-branch` - verify, present options, auto-commit (Rule 8).

## Router behavior

`route(request)` returns ordered skill ids: meta-skill first, then process
skills (`brainstorming`, `systematic-debugging`), then implementation skills.
Deterministic, no LLM, architecture-guard safe.

## Gaps / future work

- Wire `superpowers_router` into the AIOS `SkillManager` so agent dispatch
  consults it before acting (currently advisory via AGENTS.md).
- Add drill-style eval harness for the skills (Superpowers uses
  superpowers-evals); AIOS could reuse `harness/` for this.
- Port the visual-companion telemetry opt-out (`SUPERPOWERS_DISABLE_TELEMETRY`)
  semantics into AIOS observability config.
