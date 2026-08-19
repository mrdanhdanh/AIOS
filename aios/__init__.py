"""AIOS - Runtime-First, Plugin-First, Offline-First AI Operating System.

This package is the root of the AIOS monorepo. The control substrate is the
Runtime; Workers/Agents never bypass Runtime, Capability, Permission or Policy.

M0 introduced the Task Governance System (see :mod:`aios.governance`).
M1 (TASK-002) establishes the core scaffold: config, logging, metadata,
and healthcheck.
"""

__version__ = "0.2.0"
__milestone__ = "M1"
