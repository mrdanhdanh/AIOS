# Implementation artifact copy — see aios/coding_edition/integration.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-232 changes (Automated Test/Static Analysis + Code Provenance, M30):
# - CodingEdition.analyze_and_record(handler, code, work_dir, store): writes+tests
#   code via T231 path, runs py_compile static analysis, then records code
#   Evidence with full provenance (Requirement->Task->Artifact->Run->Evidence).
# - Fail-closed: requires both handler and store injected.
# Tests: test_analyze_and_record_emits_evidence, test_analyze_and_record_requires_store.
