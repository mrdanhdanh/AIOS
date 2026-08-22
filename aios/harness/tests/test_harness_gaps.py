"""Tests for harness gap implementations T029-T034."""

from __future__ import annotations

from aios.harness.contracts import HarnessArtifact, HarnessContext, HarnessEvent, HarnessReport, HarnessSpec
from aios.harness.registry import HarnessRegistry
from aios.harness.verification import EvidencePackage, ReplayEngine, VerificationPipeline
from aios.harness.test_harness import FakeRuntime, FakeTool, GoldenScenario, TestHarness, run_harness_test
from aios.harness.evaluators import (
    CompositeEvaluator, DeterministicEvaluator, EvaluationInput, HumanEvaluator,
    LLMEvaluator, SemanticEvaluator, TrajectoryVerdict, evaluate_trajectory,
)
from aios.harness.benchmark import (
    BenchmarkBaseline, BenchmarkCandidate, GateEvaluator, GateVerdict,
)
from aios.harness.readiness import DOMAIN_DOCTORS, ReadinessEngine, run_readiness


# ---- T029: Registry + contract types ----
def test_registry_register_and_duplicate():
    reg = HarnessRegistry()
    spec = HarnessSpec(spec_id="S1", name="s", version="1.0.0")
    reg.register(spec)
    assert reg.get("S1", "1.0.0") is spec
    assert reg.get_latest("S1") is spec
    try:
        reg.register(HarnessSpec(spec_id="S1", name="s", version="1.0.0"))
        assert False, "duplicate not detected"
    except ValueError:
        pass


def test_harness_contract_types():
    ctx = HarnessContext(tenant_id="t1")
    ev = HarnessEvent(kind="step")
    art = HarnessArtifact(name="a")
    rep = HarnessReport(run_id="r1", events=[ev], artifacts=[art])
    assert ctx.tenant_id == "t1"
    assert rep.to_dict()["verdict"] == "PENDING"


# ---- T030: Replay + EvidencePackage ----
def test_replay_engine_reproduces_verdict():
    engine = ReplayEngine()
    engine.record("r1", {"steps": [{"name": "a"}, {"name": "b"}], "verdict": "pass"})
    out = engine.replay("r1")
    assert out["match"] is True
    assert out["replayed_steps"] == 2


def test_evidence_package_fields():
    ev = EvidencePackage(evidence_id="e1", run_id="r1", verdict="pass", artifacts=["a1"])
    d = ev.to_dict()
    assert d["verdict"] == "pass"
    assert d["artifacts"] == ["a1"]


# ---- T031: Test harness + fakes + golden ----
def test_fake_runtime_and_golden():
    rt = FakeRuntime()
    rt.register(FakeTool("ok", result="done"))
    rt.register(FakeTool("boom", fail=True))
    harness = TestHarness(rt)
    scenario = GoldenScenario(scenario_id="g1", name="ok", steps=[{"name": "s1", "tool": "ok"}], expected_outcome="success")
    harness.add_golden(scenario)
    res = harness.run_scenario(scenario)
    assert res["match"] is True
    assert len(rt.calls) == 1


def test_run_harness_test_cli():
    scenarios = [GoldenScenario(scenario_id="g1", name="ok", steps=[{"name": "s", "tool": "ok"}], expected_outcome="success")]
    out = run_harness_test(scenarios)
    assert out["passed"] == 1


# ---- T032: Evaluators + trajectory ----
def test_deterministic_evaluator_fail():
    ev = DeterministicEvaluator()
    rep = ev.evaluate(EvaluationInput(case_id="c1", expected_output="a", actual_output="b"))
    assert rep.verdict.value == "fail"


def test_composite_evaluator_fail_closed():
    comp = CompositeEvaluator([DeterministicEvaluator(), SemanticEvaluator(threshold=0.9)])
    rep = comp.evaluate(EvaluationInput(case_id="c1", expected_output="a", actual_output="b"))
    assert rep.verdict.value == "fail"


def test_human_evaluator_no_auto_pass():
    human = HumanEvaluator(lambda inp: __import__("aios.harness.evaluators", fromlist=["EvalVerdict"]).EvalVerdict.INCONCLUSIVE)
    rep = human.evaluate(EvaluationInput(case_id="c1"))
    assert rep.verdict.value == "inconclusive"


def test_trajectory_evaluation():
    traj = [{"action": "x"}, {"action": "y"}]
    assert evaluate_trajectory(traj, traj) == TrajectoryVerdict.CORRECT
    assert evaluate_trajectory([{"action": "x"}], traj) == TrajectoryVerdict.INCORRECT


# ---- T033: GateEvaluator ----
def test_gate_evaluator_no_baseline_inconclusive():
    gate = GateEvaluator()
    rep = gate.evaluate(BenchmarkBaseline(name="b", metrics={}), BenchmarkCandidate(name="c", metrics={"x": 1.0}))
    assert rep.verdict == GateVerdict.INCONCLUSIVE


def test_gate_evaluator_regression_fail():
    gate = GateEvaluator()
    baseline = BenchmarkBaseline(name="b", metrics={"acc": 1.0})
    candidate = BenchmarkCandidate(name="c", metrics={"acc": 0.5})
    rep = gate.evaluate(baseline, candidate)
    assert rep.verdict == GateVerdict.FAIL


def test_gate_evaluator_warning():
    gate = GateEvaluator()
    baseline = BenchmarkBaseline(name="b", metrics={"acc": 1.0})
    candidate = BenchmarkCandidate(name="c", metrics={"acc": 0.85})
    rep = gate.evaluate(baseline, candidate)
    assert rep.verdict == GateVerdict.WARNING


# ---- T034: 13 domain doctors + readiness ----
def test_domain_doctors_count():
    assert len(DOMAIN_DOCTORS) == 13


def test_readiness_engine_fail_closed():
    engine = ReadinessEngine()
    report = engine.check()
    assert isinstance(report.ready, bool)
    assert report.summary["domains"] == 13
    # fail-closed: if any ERROR, not ready
    if any(c.verdict.value == "error" for c in report.checks):
        assert report.ready is False


def test_run_readiness_entrypoint():
    report = run_readiness()
    assert report.to_dict()["ready"] in (True, False)
