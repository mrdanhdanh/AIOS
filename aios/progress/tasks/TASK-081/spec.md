# TASK-081 — Asset Pipeline + Asset Capability Registry + Routing

## Objective
Xây dựng **Asset Pipeline** — quản lý lifecycle của asset (tạo, validate, version, route)
qua một **Asset Capability Registry** và cơ chế **routing** đến capability/tool xử lý asset
phù hợp. TASK-081 là asset management layer, không phải capability mới (dựa trên Capability
T001/aios/capability + Evidence T001 + Visual T080).

## Scope
**In scope:** `aios/asset_pipeline/` — AssetRecord, AssetRegistry, AssetCapabilityRegistry,
AssetRouter, AssetValidator. Tích hợp Capability + Evidence + Visual (T080).
**Out of scope:** thay thế capability system; provider/filesystem imports.

## Deliverables
- `aios/asset_pipeline/pipeline.py` — AssetRecord, AssetRegistry, AssetCapabilityRegistry, AssetRouter, AssetValidator, AssetError.
- `aios/asset_pipeline/tests/test_pipeline.py` — 7 tests (Test Matrix).
- Tích hợp Capability (aios/capability) + Evidence (T001) + Visual (T080).

## Acceptance Criteria
- Asset Registry lưu asset versioned + content_hash.
- Asset Capability Registry ánh xạ asset type → capability.
- Asset không validate → không route (fail-closed).
- Routing chỉ đến capability đủ năng lực.
- Mọi asset có provenance (T001 Rule 5).
- Cùng asset type + registry → cùng route (deterministic).
- Tích hợp được với Capability + Evidence + Visual (T080).
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T080 (Visual Evidence) → T081 → T082.
- T001 (evidence), aios/capability, T080 (visual).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `asset_pipeline` là `unknown` layer;
  chỉ import stdlib + `aios.capability` + `aios.visual_evidence`.
