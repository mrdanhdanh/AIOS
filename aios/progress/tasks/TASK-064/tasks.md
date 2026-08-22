# TASK-064 — Breakdown

- [x] Step 1 — Define `Contract` dataclass + `ContractStatus` / `ContractSurface` enums (`aios/contracts/contract.py`).
- [x] Step 2 — Implement `ContractRegistry` with register/lookup/freeze/deprecate and freeze-safety (`aios/contracts/registry.py`).
- [x] Step 3 — Add `ContractFreezeError` / `ContractNotRegisteredError` (fail-closed, no silent change).
- [x] Step 4 — Populate registry with the five 1.0 surfaces via `build_default_registry`.
- [x] Step 5 — Add conformance checks `check_contract_conformance` / `check_registry_conformance` / `require_conformance` (`aios/contracts/conformance.py`).
- [x] Step 6 — Write conformance + freeze-safety tests (`aios/contracts/tests/test_contracts.py`).
- [x] Step 7 — Run `python -m pytest aios/contracts -q` and confirm PASS.
- [x] Step 8 — Author governance artifacts (spec/critique×2/tasks/review/test/evaluation/regression) + `implementation/README.md` pointer.
