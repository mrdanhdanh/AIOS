# Regression — TASK-118

- Dependency closure: T001..T116 (M17) + TASK-118 (M18). Chạy `python -m pytest aios -q`.
- Thêm `aios/context/symbol_index.py` + tests trong `aios/context/tests/test_context.py`.
- Architecture: `context` là `unknown` (infra) layer; import sibling packages (governance.evidence/verification_integrity/security/context_optimizer) — hợp lệ, không vi phạm ARCH-001..004.
- **Result: PASS** — không regression.
