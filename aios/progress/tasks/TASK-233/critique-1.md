# TASK-233 — Critique 1

## Thiếu sót
- Spec chưa nêu rõ facade dùng `LoopController` có sẵn (T053) làm core, chỉ thêm guard.
- Chưa chỉ định signature RetryGuard phải STABLE per goal (không theo cycle_id) để lỗi lặp tích lũy.
- Chưa nêu `HaltSignal` cần `source`/`issued_at`.

## Rủi ro
- Nếu signature theo cycle_id → RetryGuard không bao giờ trigger (mỗi cycle unique).

## Đề xuất
- `UnifiedAutonomousLifecycle` wrap `LoopController` + RetryGuard (sig cố định) + KillSwitch.
- Test dùng `HaltSource.SAFETY`.
