# Implementation — TASK-082

Module: `aios/creative_domain/`
- `creative.py` — `CreativeAsset`, `VendorIntegrity`, `ReferenceAsset`, `CreativeCapabilityRegistry`, `CreativeError`.
- `tests/test_creative.py` — 7 tests (Test Matrix).

Tích hợp: import `aios.asset_pipeline` (AssetCapabilityRegistry) + `aios.visual_evidence`
(visual reference) — không rewrite asset pipeline. Mọi creative asset mang `evidence_ref`.
