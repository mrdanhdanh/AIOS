# TASK-066 — Breakdown

- [x] Step 1 — Định nghĩa `Checkpoint` dataclass (`aios/durable/checkpoint.py`) với `content_hash` deterministic + `to_dict`/`from_dict`.
- [x] Step 2 — Định nghĩa `CheckpointStore` durable (`aios/durable/store.py`): in-memory + optional file-backed, persist/load qua restart.
- [x] Step 3 — Định nghĩa `ResumeProtocol` fail-closed (`aios/durable/resume.py`): chỉ resume từ verified gần nhất, raise nếu không có.
- [x] Step 4 — Định nghĩa `IdempotencyGuard` (`aios/durable/idempotency.py`): track step đã done, `execute_once` không double side-effect.
- [x] Step 5 — Tích hợp T065/T055 (`aios/durable/integration.py`): `checkpoint_from_execution_state` + `build_resume_attempt` (strategy=RESUME).
- [x] Step 6 — Viết tests `aios/durable/tests/test_durable.py` phủ mọi AC + Test Matrix row.
- [x] Step 7 — Chạy `python -m pytest aios/durable -q` → PASS.
