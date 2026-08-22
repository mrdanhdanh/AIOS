# Critique 1 — TASK-082

- Cần làm rõ "vendor provenance": CreativeAsset.vendor_provenance (signed token/hash) —
  VendorIntegrity.verify reject nếu rỗng hoặc license không cho phép.
- Reference Asset: approve require evidence_ref; compare chỉ trên approved reference.
- CreativeCapabilityRegistry.register guard creative_type hợp lệ (image/audio/video/design).
- Đề xuất test deterministic (cùng asset+reference → cùng diff).
- Kết luận: spec đủ.
