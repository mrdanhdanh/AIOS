# Implementation — TASK-088

Module: `aios/compat_docs/`
- `docs.py` — `CompatDoc`, `DocStatus`, `DocReviewResult`, `CompatDocReviewer`.
- `tests/test_docs.py` — 7 tests (Test Matrix).

Docs/ADR: `docs/adr/ADR-Compatibility.md` + guides (versioning / migration /
backward-compat / conformance) reference T084-T087.

Tích hợp: import T084-T087 (import-level) để xác nhận docs khớp implementation
DONE; convention `docs/` + ADR (T071 DX) — không rewrite.
