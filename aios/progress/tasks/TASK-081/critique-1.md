# Critique 1 — TASK-081

- Cần làm rõ "capability" reference: AssetCapabilityRegistry lưu asset_type → list
  capability_id (string), decoupled khỏi runtime capability object → an toàn.
- Fail-closed routing: validate trước route; hash mismatch hoặc type không đăng ký → AssetError.
- Schema validation: required_fields phải có trong fields → AssetValidator.validate.
- Đề xuất test deterministic (cùng type+registry → cùng route).
- Kết luận: spec đủ.
