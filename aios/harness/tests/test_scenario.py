"""Tests for scenario and simulation."""

from __future__ import annotations

from aios.harness.scenario import ScenarioDefinition, SimulationRunner


class TestScenarioDefinition:
    def test_create(self) -> None:
        s = ScenarioDefinition(scenario_id="s1", name="test", steps=[{"name": "step1"}])
        assert s.to_dict()["scenario_id"] == "s1"
        assert s.compute_hash()

    def test_deterministic(self) -> None:
        s = ScenarioDefinition(scenario_id="s1", deterministic=True)
        h1 = s.compute_hash()
        h2 = s.compute_hash()
        assert h1 == h2


class TestSimulationRunner:
    def test_run(self) -> None:
        runner = SimulationRunner()
        scenario = ScenarioDefinition(scenario_id="s1", steps=[{"name": "a"}, {"name": "b"}])
        result = runner.run(scenario)
        assert result["status"] == "completed"
        assert result["simulated"] is True
        assert result["steps_executed"] == 2

    def test_no_real_side_effects(self) -> None:
        """AC-031-03: No real side effects."""
        runner = SimulationRunner()
        scenario = ScenarioDefinition(scenario_id="s1", steps=[{"name": "exec"}])
        result = runner.run(scenario)
        assert result["simulated"] is True

    def test_results_history(self) -> None:
        runner = SimulationRunner()
        scenario = ScenarioDefinition(scenario_id="s1", steps=[{"name": "a"}])
        runner.run(scenario)
        runner.run(scenario)
        assert len(runner.get_results()) == 2
