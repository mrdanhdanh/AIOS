from aios.evaluation.model_agent_benchmark import (
    BenchmarkReport,
    BenchmarkResult,
    ModelAgentBenchmark,
)
from aios.evaluation._common import EvaluationError


def test_benchmark_construction_immutable():
    r = BenchmarkResult("R1", "case", "PASS")
    assert r.result_id == "R1"


def test_benchmark_pass_all_pass():
    b = ModelAgentBenchmark()
    rep = b.run([BenchmarkResult("R1", "c", "PASS"), BenchmarkResult("R2", "c", "PASS")])
    assert isinstance(rep, BenchmarkReport)
    assert rep.status == "PASS"
    assert rep.breaches == 0


def test_benchmark_insufficient_on_breach():
    b = ModelAgentBenchmark()
    rep = b.run([BenchmarkResult("R1", "c", "PASS"), BenchmarkResult("R2", "c", "BREACH")])
    assert rep.status == "INSUFFICIENT"
    assert rep.breaches == 1


def test_benchmark_unknown_on_unknown():
    b = ModelAgentBenchmark()
    rep = b.run([BenchmarkResult("R1", "c", "PASS"), BenchmarkResult("R2", "c", "UNKNOWN")])
    assert rep.status == "UNKNOWN"


def test_benchmark_rejects_invalid_status():
    b = ModelAgentBenchmark()
    try:
        b.run([BenchmarkResult("R1", "c", "NOPE")])
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_benchmark_rejects_non_result():
    b = ModelAgentBenchmark()
    try:
        b.run(["not-a-result"])
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_benchmark_deterministic_report_id():
    b = ModelAgentBenchmark()
    a = b.run([BenchmarkResult("R1", "c", "PASS")])
    c = b.run([BenchmarkResult("R1", "c", "PASS")])
    assert a.report_id == c.report_id
