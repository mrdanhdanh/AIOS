"""AIOS - Runtime-First, Plugin-First, Offline-First AI Operating System.

This package is the root of the AIOS monorepo. The control substrate is the
Runtime; Workers/Agents never bypass Runtime, Capability, Permission or Policy.

M0 introduces the Task Governance System (see :mod:`aios.governance`) which is
the self-verifying control plane for AIOS development. From TASK-002 onward,
every task is enforced through this governance system.
"""

__version__ = "0.1.0"
__milestone__ = "M0"
