# Implementation artifact copy — see aios/coder/contract.py (canonical).
# Satisfies STATE_ARTIFACTS mapping (IMPLEMENTING: implementation/).

# TASK-230 changes (Coder Agent <-> Capability Registry, M30):
# - CoderCapabilityResolver(contract, registry): capability-injected wiring.
# - resolve(capability): fails closed if not declared on contract (ARCH-004)
#   or not present in CapabilityRegistry (no guessing, no direct I/O).
# - is_resolvable(): non-raising variant.
# Tests: test_resolver_resolves_declared_and_registered,
#        test_resolver_fails_when_not_declared,
#        test_resolver_fails_when_not_registered (aios/coder/tests/test_coder.py).
