# Breakdown — TASK-223

1. **Governance fix (meta):** add `runtime_utilization` gate + wire into `gate_check.py`.
   - `aios/governance/runtime_utilization/checker.py`
   - register in `aios/governance/cli/gate_check.py`
2. **AIOS tool:** `aios/tool/website/n5_builder.py` generates site + evidence.
3. **Generator script:** `implementation/build_n5_site.py` invokes the AIOS tool.
4. **Real harness:** `implementation/harness_n5.js` (Node) verifies behavior.
5. **Pytest:** `implementation/test_website.py` runs AIOS build + Node harness.
6. **Generate artifacts:** run builder to emit `index.html`, `css/`, `js/`, `build_evidence.json`.
7. **Docs:** spec/critique×2/review/test/evaluation/regression with `Demonstrates-AIOS: true`.
8. **Verify:** `pytest` + `gate_check.py --task TASK-223` → all PASS.
