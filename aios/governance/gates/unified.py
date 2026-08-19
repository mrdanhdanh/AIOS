"""Unified task gate implementation (convergence of the 7 rules)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class GateComponent:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class GateResult:
    passed: bool
    components: List[GateComponent] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        for c in self.components:
            mark = "PASS" if c.passed else "FAIL"
            lines.append(f"  [{mark}] {c.name}: {c.detail}")
        overall = "PASS" if self.passed else "BLOCKED"
        return f"Unified Gate: {overall}\n" + "\n".join(lines)


class UnifiedTaskGate:
    """Aggregates component gates.

    Each component is a callable ``(ctx) -> GateComponent``. The unified gate
    passes only when every component passes (logical AND). If a component is
    missing/raises, it is recorded as a failure so the gate fails closed.
    """

    def __init__(self) -> None:
        self._components: Dict[str, Callable[[dict], GateComponent]] = {}

    def register(self, name: str, checker: Callable[[dict], GateComponent]) -> None:
        self._components[name] = checker

    def evaluate(self, context: Optional[dict] = None) -> GateResult:
        ctx = context or {}
        components: List[GateComponent] = []
        for name, checker in self._components.items():
            try:
                comp = checker(ctx)
            except Exception as exc:  # fail closed
                comp = GateComponent(name, False, f"checker error: {exc}")
            components.append(comp)
        passed = all(c.passed for c in components)
        return GateResult(passed=passed, components=components)
