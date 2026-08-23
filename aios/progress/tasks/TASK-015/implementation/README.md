# TASK-015 Implementation — Plugin / Skill Execution

Implementation lives in `aios/skill/` (M2 P4 — Plugin/Skill Execution).

```
aios/skill/
  contracts.py   # SkillContract, SkillStatus, SkillTransition, SkillPersistentState, SKILL_CONTRACT
  registry.py    # SkillRegistry (register/resolve/enable/disable, persistent state)
  resolver.py    # SkillDependencyResolver, ResolverError (dependency resolution)
  sandbox.py     # Sandbox, SandboxPool, SandboxStatus (sandbox pool, reset between executions)
  manager.py     # SkillManager (lifecycle orchestration, rollback to certified state)
  __init__.py    # re-exports
  tests/
    test_contracts.py
    test_registry.py
    test_resolver.py
    test_manager.py
    test_sandbox.py
    test_architecture.py
```

Lifecycle: `RESOLVE → VALIDATE → INSTALL → ENABLE → [READY] → DISABLE → UNLOAD → RELOAD → UPGRADE → ROLLBACK → REMOVE` (deterministic, policy-checked, offline-first).

See `../spec.md`, `../test.md`, `../evaluation.md`, `../regression.md` for acceptance, verification and regression evidence. Full suite: `python -m pytest aios -q` (1257 PASS at M2, 2477 PASS current).
