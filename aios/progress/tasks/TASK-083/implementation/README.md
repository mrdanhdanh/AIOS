# Implementation — TASK-083

Module: `aios/skill_distiller/`
- `distiller.py` — `DistilledSkill`, `SkillDistiller`, `StaticPackage`, `StaticDeploy`, `DistillerError`.
- `tests/test_distiller.py` — 6 tests (Test Matrix).

Tích hợp: import `aios.governance.architecture.guard` (scan_source cho T063 conformance)
+ `aios.skill` (contract abstraction) + `aios.devkit` (packaging concept). Static deploy
fail-closed trên contract/guard/dynamic-dependency. Mọi skill mang `evidence_ref`.
