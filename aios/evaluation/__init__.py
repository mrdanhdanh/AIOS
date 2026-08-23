"""aios.evaluation — M25 Evaluation & Benchmark.

Twelve deterministic, fail-closed, provenance-bearing evaluation components that
compose into a Continuous Evaluation harness. Each component is an independent
capability (unknown/infra layer) with its own immutable result type.
"""

from __future__ import annotations

from aios.evaluation._common import EvaluationError, _hash, _now, redact_secret
from aios.evaluation.evaluation_contract import (
    ContractValidationReport,
    EvaluationContract,
    EvaluationContractValidator,
)
from aios.evaluation.evaluation_engine import (
    DimensionScore,
    EvaluationEngine,
    ScoreReport,
)
from aios.evaluation.quality_dimensions import (
    DimensionReport,
    QualityDimension,
    QualityDimensionEvaluator,
)
from aios.evaluation.benchmark_registry import (
    Benchmark,
    BenchmarkRegistry,
    RegistryReport,
)
from aios.evaluation.baseline_manager import (
    Baseline,
    BaselineManager,
    BaselineReport,
)
from aios.evaluation.regression_detector import (
    RegressionCheck,
    RegressionDetector,
    RegressionReport,
)
from aios.evaluation.agent_behavior_evaluator import (
    AgentBehaviorEvaluator,
    BehaviorEvalReport,
    BehaviorSpec,
)
from aios.evaluation.efficiency_evaluator import (
    EfficiencyBudget,
    EfficiencyEvaluator,
    EfficiencyReport,
)
from aios.evaluation.failure_attribution import (
    AttributionReport,
    Failure,
    FailureAttributor,
)
from aios.evaluation.evaluation_store import (
    EvaluationStore,
    StoredEvaluation,
    StoreReport,
)
from aios.evaluation.model_agent_benchmark import (
    BenchmarkReport,
    BenchmarkResult,
    ModelAgentBenchmark,
)
from aios.evaluation.continuous_evaluation import (
    ContinuousEvaluation,
    ContinuousReport,
)
