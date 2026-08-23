# Regression — TASK-110

- Dependency closure: T001..T112 (toàn M0-M16). Chạy `python -m pytest aios -q`.
- Thêm `aios/model_runtime/provider_registry.py` + tests trong `aios/model_runtime/tests/test_model_runtime.py`.
- Architecture: `model_runtime` là `unknown` (infra) layer; import sibling packages (identity/security/certification/integrity/quota/evidence) — hợp lệ, không vi phạm ARCH-001..004.
- **Result: PASS** — không regression.
