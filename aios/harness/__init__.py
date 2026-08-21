"""AIOS verification / test harness (M6).

The harness is independent of the Runtime and produces replayable evidence.
Provides: contracts, kernel lifecycle, verification, scenarios, evaluation,
benchmarking, and doctor/readiness subsystems.
"""

from aios.harness.contracts import Assertion, HarnessRun, HarnessSpec, RunResult, RunStatus
from aios.harness.kernel import HarnessKernel
from aios.harness.verification import EvidencePackage, VerificationPipeline, Verdict
from aios.harness.scenario import ScenarioDefinition, SimulationRunner
from aios.harness.evaluation import EvaluationCase, EvaluationResult, EvaluationSuite, Metric
from aios.harness.benchmark import BenchmarkRun, BaselineManager, RegressionDetector
from aios.harness.doctor import HarnessDoctor, ReadinessChecker

__all__ = [
    "Assertion", "HarnessSpec", "HarnessRun", "RunResult", "RunStatus",
    "HarnessKernel", "EvidencePackage", "VerificationPipeline", "Verdict",
    "ScenarioDefinition", "SimulationRunner",
    "EvaluationCase", "EvaluationResult", "EvaluationSuite", "Metric",
    "BenchmarkRun", "BaselineManager", "RegressionDetector",
    "HarnessDoctor", "ReadinessChecker",
]
