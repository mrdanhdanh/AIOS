# TASK-083 — SkillDistiller + Static Deploy

## Objective
Xây dựng **SkillDistiller** — trích xuất (distill) một workflow / agent behavior thành một
**Skill** có thể tái sử dụng, và **Static Deploy** — đóng gói skill để deploy mà không cần
runtime động. TASK-083 là skill packaging, không phải agent framework mới (dựa trên Skill
T015/aios/skill + Devkit T071 + Contract T064 + Architecture guard T063).

## Scope
**In scope:** `aios/skill_distiller/` — DistilledSkill, SkillDistiller, StaticPackage,
StaticDeploy. Tích hợp Skill (aios/skill) + Devkit (T071) + Contract (T064) + Guard (T063).
**Out of scope:** thay thế skill system; dynamic runtime; provider/filesystem imports.

## Deliverables
- `aios/skill_distiller/distiller.py` — DistilledSkill, SkillDistiller, StaticPackage, StaticDeploy, DistillerError.
- `aios/skill_distiller/tests/test_distiller.py` — 6 tests (Test Matrix).
- Tích hợp Skill (aios/skill) + Devkit (T071) + Contract (T064) + Guard (T063).

## Acceptance Criteria
- Distiller trích xuất workflow/behavior thành Skill có contract.
- Skill conform public contract 1.0 (T064).
- Static package self-contained (không dynamic runtime).
- Static deploy qua architecture guard (T063).
- Mọi skill có provenance (T001 Rule 5).
- Cùng workflow + distiller → cùng skill (deterministic).
- Tích hợp được với Skill + Devkit + Contract.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T082 (Creative Domain) → T083 (đóng M11) → T084 (M12).
- T015 (skill), T071 (devkit), T064 (contract), T063 (architecture guard).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `skill_distiller` là `unknown` layer;
  import `aios.governance.architecture.guard` (unknown) + `aios.skill` (skill layer, allowed).
