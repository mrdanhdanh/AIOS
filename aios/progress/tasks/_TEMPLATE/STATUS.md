# Lifecycle Status — TASK-xxx
#
# `state:` MUST be a single valid value from the lifecycle state machine
# (aios/governance/lifecycle/statemachine.py), NOT a menu:
#   PLANNED | SPECIFIED | CRITIQUED_1 | CRITIQUED_2 | BROKEN_DOWN | REVIEWED
#   | IMPLEMENTING | TESTING | EVALUATING | REGRESSION | READY_TO_CLOSE | DONE
# The gate (gate_check.py) reads `state:` directly; an invalid value => lifecycle FAIL.

state: PLANNED
current: PLANNED

gate: pending `python ../../scripts/gate_check.py TASK-xxx`
