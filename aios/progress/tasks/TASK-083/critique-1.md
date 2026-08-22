# Critique 1 — TASK-083

- Cần làm rõ "contract 1.0": DistilledSkill.contract_version = "1.0.0"; StaticDeploy.deploy
  reject nếu != 1.0.0 (T064).
- Static package self-contained: StaticPackage.is_self_contained reject nếu import
  subprocess/os/importlib/eval/exec (dynamic runtime).
- Architecture conformance: StaticDeploy gọi scan_source (guard T063) → reject nếu có
  violation (vd skill-layer import provider adapter).
- Đề xuất test deterministic (cùng workflow → cùng skill).
- Kết luận: spec đủ.
