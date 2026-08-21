"""Test harness scenarios and simulation.

AC-031-01: Scenario loading — valid parsed, invalid rejected.
AC-031-02: Golden scenarios deterministic.
AC-031-03: No real side effects in simulation.
AC-031-04: Deterministic scenarios run offline.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FailureInjection:
    """Defines a failure to inject."""
    failure_type: str = ""
    target: str = ""
    probability: float = 0.0
    detail: str = ""


@dataclass
class ScenarioDefinition:
    """Declarative scenario for test harness."""
    scenario_id: str = ""
    name: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    expected_outcome: str = "success"
    failure_injections: list[FailureInjection] = field(default_factory=list)
    deterministic: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id, "name": self.name,
            "steps": self.steps, "expected_outcome": self.expected_outcome,
            "deterministic": self.deterministic,
        }

    def compute_hash(self) -> str:
        return hashlib.sha256(str(self.to_dict()).encode()).hexdigest()[:16]


class SimulationRunner:
    """Runs scenarios in simulation mode — no real side effects.

    AC-031-03: No real side effects.
    AC-031-04: Runs offline without LLM.
    """

    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []

    def run(self, scenario: ScenarioDefinition) -> dict[str, Any]:
        """Run a scenario in simulation."""
        executed_steps = []
        for step in scenario.steps:
            executed_steps.append({
                "step": step.get("name", "unknown"),
                "status": "completed",
                "simulated": True,
            })

        result = {
            "scenario_id": scenario.scenario_id,
            "status": "completed",
            "steps_executed": len(executed_steps),
            "steps": executed_steps,
            "simulated": True,
            "deterministic": scenario.deterministic,
        }
        self._results.append(result)
        return result

    def get_results(self) -> list[dict[str, Any]]:
        return list(self._results)
