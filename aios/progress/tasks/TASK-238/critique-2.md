# TASK-238 — Critique 2

## Thiếu sót
- Cần đảm bảo regression gate là fail-closed (regression_pass=False -> REJECTED).

## Rủi ro
- Thiếu regression -> promote change chưa được validate đầy đủ.

## Đề xuất
- Bước 5 regression: `not regression_pass` -> phase REGRESSION, promoted=False.
- Thêm test `test_lifecycle_rejects_on_failed_regression`.
