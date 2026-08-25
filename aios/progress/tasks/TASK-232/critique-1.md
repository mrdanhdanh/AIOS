# TASK-232 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ static-analysis dùng gì (`py_compile`) và Evidence phải có provenance chain complete.
- Chưa chỉ định `analyze_and_record` fail-closed khi thiếu `store`.

## Rủi ro
- Nếu không ghi Evidence → M32 (Evidence-Native) không có dữ liệu code.

## Đề xuất
- `analyze_and_record`: write+test (T231) → py_compile → record Evidence (Requirement→Task→Artifact→Run→Evidence).
- Fail-closed nếu thiếu handler/store.
