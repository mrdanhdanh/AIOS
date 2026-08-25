# TASK-237 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ Control Center là READ-ONLY aggregation (frontend chỉ render).
- Chưa chỉ định fail-isolated per plane (1 plane lỗi không crash snapshot).

## Rủi ro
- Nếu aggregator raise khi 1 subsystem down → toàn bộ dashboard sập.

## Đề xuất
- `ControlCenterAggregator` thu thập từng plane độc lập, lỗi → entry `error`.
- Router `/control-center` chỉ trả snapshot, không mutate.
