# TASK-082 — Creative Domain + Vendor Integrity + Reference Asset

## Objective
Mở rộng AIOS sang **Creative Domain** — xử lý asset sáng tạo (hình ảnh, âm thanh, video,
design) với **Vendor Integrity** (xác thực nguồn vendor / model sinh asset) và **Reference
Asset** (asset tham chiếu chuẩn để so sánh). TASK-082 là creative-domain extension, không
phải runtime rewrite (dựa trên Asset Pipeline T081 + Evidence T001 + Visual T080).

## Scope
**In scope:** `aios/creative_domain/` — CreativeAsset, VendorIntegrity, ReferenceAsset,
CreativeCapabilityRegistry. Tích hợp Asset Pipeline (T081) + Evidence + Visual (T080).
**Out of scope:** thay thế asset pipeline; render engine; provider/filesystem imports.

## Deliverables
- `aios/creative_domain/creative.py` — CreativeAsset, VendorIntegrity, ReferenceAsset, CreativeCapabilityRegistry, CreativeError.
- `aios/creative_domain/tests/test_creative.py` — 7 tests (Test Matrix).
- Tích hợp Asset Pipeline (T081) + Evidence (T001) + Visual (T080).

## Acceptance Criteria
- Creative Asset Types định nghĩa schema đầy đủ (image/audio/video/design).
- Asset thiếu vendor provenance → reject (fail-closed, Vendor Integrity).
- Reference Asset được duyệt trước khi so sánh.
- License vi phạm → reject.
- Mọi creative asset có provenance (T001 Rule 5).
- Cùng asset + reference → cùng so sánh (deterministic).
- Tích hợp được với Asset Pipeline + Evidence + Visual.
- Regression của các milestone trước PASS; không vi phạm invariants.

## Dependencies
- T081 (Asset Pipeline) → T082 → T083.
- T081 (asset pipeline), T001 (evidence), T080 (visual).

## Governance references
- Rule 1..7 via `aios/governance/*`. Architecture: `creative_domain` là `unknown` layer;
  chỉ import stdlib + `aios.asset_pipeline` + `aios.visual_evidence`.
