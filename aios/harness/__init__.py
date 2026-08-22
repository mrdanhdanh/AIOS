"""AIOS verification / test harness (M6).

The harness is independent of the Runtime and produces replayable evidence.
Provides: contracts, kernel lifecycle, verification, scenarios, evaluation,
benchmarking, and doctor/readiness subsystems.
"""

from aios.harness.contracts import (
    Assertion, HarnessArtifact, HarnessContext, HarnessEvent, HarnessReport,
    HarnessRun, HarnessSpec, RunResult, RunStatus,
)
from aios.harness.kernel import HarnessKernel
from aios.harness.registry import HarnessRegistry
from aios.harness.verification import EvidencePackage, ReplayEngine, VerificationPipeline, Verdict
from aios.harness.scenario import ScenarioDefinition, SimulationRunner
from aios.harness.test_harness import FakeRuntime, FakeTool, GoldenScenario, TestHarness
from aios.harness.evaluation import EvaluationCase, EvaluationResult, EvaluationSuite, Metric
from aios.harness.evaluators import (
    CompositeEvaluator, DeterministicEvaluator, EvaluationInput, EvaluationReport,
    Evaluator, HumanEvaluator, LLMEvaluator, MetricResult, SemanticEvaluator,
    TrajectoryVerdict, evaluate_trajectory,
)
from aios.harness.benchmark import (
    BaselineManager, BenchmarkBaseline, BenchmarkCandidate, BenchmarkReport,
    BenchmarkRun, GateEvaluator, GateVerdict, RegressionDetector,
)
from aios.harness.doctor import HarnessDoctor, ReadinessChecker
from aios.harness.readiness import DOMAIN_DOCTORS, ReadinessEngine, ReadinessReport, run_readiness

__all__ = [
    "Assertion", "HarnessSpec", "HarnessRun", "RunResult", "RunStatus",
    "HarnessContext", "HarnessEvent", "HarnessArtifact", "HarnessReport",
    "HarnessKernel", "HarnessRegistry", "EvidencePackage", "ReplayEngine",
    "VerificationPipeline", "Verdict",
    "ScenarioDefinition", "SimulationRunner",
    "FakeRuntime", "FakeTool", "GoldenScenario", "TestHarness",
    "EvaluationCase", "EvaluationResult", "EvaluationSuite", "Metric",
    "Evaluator", "EvaluationInput", "EvaluationReport", "MetricResult",
    "DeterministicEvaluator", "SemanticEvaluator", "LLMEvaluator", "HumanEvaluator",
    "CompositeEvaluator", "TrajectoryVerdict", "evaluate_trajectory",
    "BenchmarkRun", "BaselineManager", "RegressionDetector",
    "BenchmarkBaseline", "BenchmarkCandidate", "BenchmarkReport",
    "GateEvaluator", "GateVerdict",
    "HarnessDoctor", "ReadinessChecker",
    "DOMAIN_DOCTORS", "ReadinessEngine", "ReadinessReport", "run_readiness",
]
