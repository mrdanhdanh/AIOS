# TASK-015 — Evaluation

Verdict: **PASS** — all 12 acceptance criteria satisfied.

| AC | Requirement | Evidence |
|----|-------------|----------|
| AC-015-01 | Skill is extension, not Core | `aios/skill/` layer imports only stdlib + `aios.core` |
| AC-015-02 | Skill never bypasses Runtime/Capability/Permission/Policy | runtime services injected; manager enforces before side effects |
| AC-015-03 | Lifecycle deterministic & manageable | `VALID_TRANSITIONS` enforced; invalid transition rejected |
| AC-015-04 | Dependency resolution before enable/exec | `SkillDependencyResolver` (direct+transitive, constraints, cycle FAIL) |
| AC-015-05 | Install/Upgrade/Remove preserve certified state | `_certified`/`_previous_version` backups; rollback restores |
| AC-015-06 | Rollback to prior certified version/state | `rollback()` restores version/manifest/deps/caps/config; health check |
| AC-015-07 | Sandbox reused but state reset between runs | `Sandbox.reset()` RUNNING->RESETTING->READY; state leakage tested |
| AC-015-08 | Offline-first lifecycle | no LLM/network; deterministic, thread-safe RLock |
| AC-015-09 | State persists across restart | `persist()`/`_persistent`; DISABLED not auto-ENABLED |
| AC-015-10 | Capability integration via TASK-014 layer | capability_registry injected; registers caps on enable |
| AC-015-11 | Install failure cleanup, no active-version corruption | install wrapped; temp state cleaned; active kept |
| AC-015-12 | Kernel wiring + health snapshot | `RuntimeKernel` wires SkillRegistry/SandboxPool/SkillManager (step 15.7) |

No architecture violations detected by the T016 gate.
