# Critique 2 — TASK-081

- Đồng tình critique 1. AssetRouter.route fail-closed đúng (raise thay vì route rỗng).
- Cần đảm bảo policy selection chỉ chọn capability đã đăng ký → đã check `policy in capable`.
- Architecture: `unknown` layer, import `aios.capability` (capability layer, allowed) → an toàn.
- Kết luận: PASS.
