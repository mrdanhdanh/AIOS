"""Test harness — fake runtime/tool, golden scenarios, deterministic runners (T031)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class FakeTool:
    """A deterministic fake tool for test harness (no real side effects)."""
    name: str
    result: Any = "ok"
    fail: bool = False

    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        if self.fail:
            raise RuntimeError(f"FakeTool {self.name} failed")
        return self.result


@dataclass
class FakeRuntime:
    """A deterministic fake runtime that records calls (no real side effects)."""
    tools: dict[str, FakeTool] = field(default_factory=dict)
    calls: list[dict[str, Any]] = field(default_factory=list)

    def register(self, tool: FakeTool) -> None:
        self.tools[tool.name] = tool

    def execute(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        if tool_name not in self.tools:
            raise KeyError(f"Unknown tool {tool_name}")
        self.calls.append({"tool": tool_name, "args": args, "kwargs": kwargs})
        return self.tools[tool_name].invoke(*args, **kwargs)


@dataclass
class GoldenScenario:
    """A golden (reference) scenario with a known expected outcome."""
    scenario_id: str
    name: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    expected_outcome: str = "success"

    def fingerprint(self) -> str:
        payload = str({"steps": self.steps, "expected_outcome": self.expected_outcome})
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


class TestHarness:
    """Runs scenarios against a fake runtime deterministically (offline)."""

    def __init__(self, runtime: FakeRuntime | None = None) -> None:
        self.runtime = runtime or FakeRuntime()
        self._golden: dict[str, GoldenScenario] = {}

    def add_golden(self, scenario: GoldenScenario) -> None:
        self._golden[scenario.scenario_id] = scenario

    def run_scenario(self, scenario: GoldenScenario) -> dict[str, Any]:
        executed = []
        for step in scenario.steps:
            tool = step.get("tool")
            if tool:
                if tool not in self.runtime.tools:
                    self.runtime.register(FakeTool(tool, result="ok"))
                self.runtime.execute(tool, *step.get("args", []), **step.get("kwargs", {}))
            executed.append(step.get("name", "step"))
        outcome = "success" if not any(
            self.runtime.tools.get(s.get("tool", ""), FakeTool("x")).fail
            for s in scenario.steps if s.get("tool")
        ) else "failure"
        return {
            "scenario_id": scenario.scenario_id,
            "executed_steps": executed,
            "outcome": outcome,
            "expected": scenario.expected_outcome,
            "match": outcome == scenario.expected_outcome,
        }

    def run_all_golden(self) -> list[dict[str, Any]]:
        return [self.run_scenario(s) for s in self._golden.values()]


def run_harness_test(scenarios: list[GoldenScenario]) -> dict[str, Any]:
    """CLI entry: run a set of golden scenarios and report (aiagent harness test)."""
    harness = TestHarness()
    for s in scenarios:
        harness.add_golden(s)
    results = harness.run_all_golden()
    passed = sum(1 for r in results if r["match"])
    return {"total": len(results), "passed": passed, "results": results}
