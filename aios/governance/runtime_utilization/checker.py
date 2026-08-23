"""Runtime-utilization checker (Rule: demonstrates-AIOS must exercise AIOS).

Motivation
----------
TASK-222 was a "system test of the governance pipeline" whose ``spec.md``
explicitly stated *"No AIOS runtime dependency"* and still reached DONE. The
old ``gate_check.py`` only verified artifact presence + architecture + CI, so a
static deliverable could be wrapped in governance paperwork without AIOS ever
running. This checker makes that impossible for tasks that claim to
*demonstrate* or *prove* AIOS.

Trigger
-------
The checker activates when ``spec.md`` contains the front-matter marker::

    Demonstrates-AIOS: true

(or when called with ``required=True`` for audits). When active, the
``implementation/`` tree MUST contain:

1. Real AIOS usage — an ``from aios...`` / ``import aios`` statement, or a
   reference to a core AIOS construct (``DeterministicControlPath``,
   ``CapabilityRegistry``, ``ArchitectureGuard``, ``VerificationResult``,
   ``EvidencePackage``, or any ``aios.<layer>`` package).
2. AIOS-produced provenance — a ``build_evidence.json`` (or similar) written
   by the AIOS build, carrying a ``producer`` that starts with ``aios`` and a
   ``content_hash``.

If either is missing the gate FAILS (fail-closed).
"""

from __future__ import annotations

import os
import re
from typing import List, Optional, Tuple

from aios.governance.gates import GateComponent

MARKER = re.compile(r"^\s*Demonstrates-AIOS:\s*true\s*$", re.MULTILINE | re.IGNORECASE)

# Patterns that prove the deliverable actually ran through AIOS.
AIOS_USAGE_PATTERNS: List[re.Pattern] = [
    re.compile(r"^\s*(from|import)\s+aios\b", re.MULTILINE),
    re.compile(r"DeterministicControlPath"),
    re.compile(r"CapabilityRegistry"),
    re.compile(r"ArchitectureGuard"),
    re.compile(r"VerificationResult|EvidencePackage"),
    re.compile(r"aios\.harness|aios\.runtime|aios\.capability|aios\.governance|aios\.tool|aios\.deterministic"),
]

EVIDENCE_FILE_RE = re.compile(r"build_evidence\.json$", re.IGNORECASE)


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _scan_aios_usage(root: str) -> List[Tuple[str, str]]:
    """Return (filename, matched-pattern) for files showing AIOS usage."""
    hits: List[Tuple[str, str]] = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith((".py", ".js", ".ts")):
                continue
            text = _read(os.path.join(dirpath, fn))
            for pat in AIOS_USAGE_PATTERNS:
                m = pat.search(text)
                if m:
                    hits.append((fn, m.group(0)))
                    break
    return hits


def _find_evidence(root: str) -> Optional[str]:
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if EVIDENCE_FILE_RE.search(fn):
                return os.path.join(dirpath, fn)
    return None


def _evidence_valid(path: str) -> bool:
    import json

    try:
        data = json.loads(_read(path))
    except (OSError, ValueError):
        return False
    producer = str(data.get("producer", ""))
    content_hash = str(data.get("content_hash", ""))
    return producer.lower().startswith("aios") and bool(content_hash)


def check(task_dir: str, required: Optional[bool] = None) -> GateComponent:
    """Evaluate runtime-utilization for a task folder.

    ``required`` forces activation (used by audits to prove the loophole is
    now detectable on legacy tasks such as TASK-222).
    """
    spec = _read(os.path.join(task_dir, "spec.md"))
    triggered = bool(MARKER.search(spec))
    if required is not None:
        triggered = triggered or required
    if not triggered:
        return GateComponent(
            "runtime_utilization", True,
            "not a demonstrates-AIOS task; skipped",
        )

    impl = os.path.join(task_dir, "implementation")
    if not os.path.isdir(impl):
        return GateComponent(
            "runtime_utilization", False,
            "Demonstrates-AIOS set but no implementation/ to scan",
        )

    usage = _scan_aios_usage(impl)
    if not usage:
        return GateComponent(
            "runtime_utilization", False,
            "Demonstrates-AIOS but NO aios.* usage found in implementation/ "
            "(deliverable does not actually exercise AIOS)",
        )

    ev_path = _find_evidence(impl)
    if ev_path is None or not _evidence_valid(ev_path):
        return GateComponent(
            "runtime_utilization", False,
            "Demonstrates-AIOS but no valid build_evidence.json "
            "(AIOS-produced provenance with producer=aios.* + content_hash) found",
        )

    return GateComponent(
        "runtime_utilization", True,
        f"AIOS exercised: {len(usage)} file(s) with aios usage + valid build_evidence.json",
    )


class RuntimeUtilizationCheck:
    """Callable wrapper so the gate can register ``check(task_dir)``."""

    def __call__(self, task_dir: str) -> GateComponent:
        return check(task_dir)
