# TASK-066 Implementation

Source code thực tế của TASK-066 nằm trong package **`aios/durable/`** (không duplicate code ở đây):

| Module | Nội dung |
|--------|----------|
| `aios/durable/__init__.py` | Public exports: `Checkpoint`, `CheckpointStore`, `ResumeProtocol`, `ResumeError`, `IdempotencyGuard`, `StepOutcome`. |
| `aios/durable/checkpoint.py` | `Checkpoint` dataclass (execution_id, step_id, state_hash, verified, created_at, evidence_ref) + `content_hash` deterministic. |
| `aios/durable/store.py` | `CheckpointStore` — in-memory + optional file-backed, persist qua restart. |
| `aios/durable/resume.py` | `ResumeProtocol` + `ResumeError` — fail-closed resume chỉ từ verified gần nhất. |
| `aios/durable/idempotency.py` | `IdempotencyGuard` + `StepOutcome` — không re-execute step đã done. |
| `aios/durable/integration.py` | Glue T065 (`aios.runtime.state`) + T055 (`aios.autonomous_recovery.contracts`): `checkpoint_from_execution_state`, `build_resume_attempt`, `runtime_state_hash`. |
| `aios/durable/tests/test_durable.py` | 14 tests phủ mọi AC + Test Matrix row. |

Chạy tests:
```
python -m pytest aios/durable -q
```
