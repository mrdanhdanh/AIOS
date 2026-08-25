# Implementation artifact copy — see aios/coding_edition/integration.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-231 changes (CodingEdition <-> RealToolHandler, M30):
# - CodingEdition.execute_code(handler, generated_code, work_dir, run_tests=False):
#   writes generated_code to <work_dir>/generated_code.py THROUGH the injected
#   RealToolHandler (policy/permission/sandbox enforced, fail-closed), optionally
#   runs a test command, and returns a verification_report string.
# - No direct file I/O in the agent; every mutation routes via RealToolHandler.
# Tests: test_execute_code_writes_via_handler, test_execute_code_requires_handler,
#        test_execute_code_denied_without_permission (test_coding_edition.py).
