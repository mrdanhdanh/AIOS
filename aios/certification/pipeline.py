"""Certification checks pipeline — runs checks, produces evidence + signature."""

from __future__ import annotations

import hashlib
import time
from typing import Callable

from aios.certification.contracts import CertCheck, CertStatus


class CertPipeline:
    """Runs a set of named checks against a target; fails closed on any failure."""

    def __init__(self) -> None:
        self._checks: dict[str, Callable[[str], CertCheck]] = {}

    def register_check(self, name: str, fn: Callable[[str], CertCheck]) -> None:
        self._checks[name] = fn

    def run(self, target_id: str, check_names: list[str]) -> tuple[bool, list[CertCheck], str]:
        """Return (all_passed, checks, signature). Fail-closed."""
        results: list[CertCheck] = []
        for name in check_names:
            fn = self._checks.get(name)
            if fn is None:
                results.append(CertCheck(name=name, passed=False, detail="unknown check"))
            else:
                results.append(fn(target_id))
        all_passed = all(c.passed for c in results)
        evidence = [f"{c.name}:{'pass' if c.passed else 'fail'}" for c in results]
        payload = "|".join(evidence) + f"|{target_id}"
        signature = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return all_passed, results, signature
