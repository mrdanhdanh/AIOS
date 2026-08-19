"""AIOS Task Governance System.

Self-verifying enforcement of the 7 General Rules (Quy tắc chung):
  Rule 1  immutable IDs          -> task_registry
  Rule 2  dependency ordering    -> dependency
  Rule 3  no Runtime bypass      -> architecture
  Rule 4  deterministic-first    -> deterministic
  Rule 5  evidence provenance    -> evidence
  Rule 6  lifecycle gate         -> lifecycle
  Rule 7  regression of deps     -> regression
Unified decision: gates.gate.TaskGate
"""
