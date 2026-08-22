# Task Breakdown — TASK-081

- [x] AssetRecord dataclass (asset_id, asset_type, version, content_hash, capable_capabilities, evidence_ref).
- [x] AssetRegistry (versioned store, get/latest).
- [x] AssetCapabilityRegistry (asset_type → capability ids).
- [x] AssetValidator (hash + schema, fail-closed).
- [x] AssetRouter.route (policy-driven, fail-closed).
- [x] Tests 7 cases (Test Matrix).
- [x] Tích hợp Capability + Evidence + Visual (import-level).
