# Implementation — TASK-081

Module: `aios/asset_pipeline/`
- `pipeline.py` — `AssetRecord`, `AssetRegistry`, `AssetCapabilityRegistry`, `AssetRouter`, `AssetValidator`, `AssetError`.
- `tests/test_pipeline.py` — 7 tests (Test Matrix).

Tích hợp: import `aios.capability` (registry abstraction) + `aios.visual_evidence`
(visual asset types) — không rewrite capability system. Mọi asset mang `evidence_ref`.
