from aios.evaluation.benchmark_registry import (
    Benchmark,
    BenchmarkRegistry,
    RegistryReport,
)
from aios.evaluation._common import EvaluationError


def test_registry_construction():
    r = BenchmarkRegistry()
    assert isinstance(r, BenchmarkRegistry)


def test_registry_register_pass():
    r = BenchmarkRegistry()
    rep = r.register(Benchmark("B1", "suite-a", "unit"))
    assert isinstance(rep, RegistryReport)
    assert rep.status == "PASS"
    assert rep.found == "B1"


def test_registry_lookup_unknown_returns_unknown():
    r = BenchmarkRegistry()
    rep = r.lookup("missing")
    assert rep.status == "UNKNOWN"
    assert rep.found is None


def test_registry_rejects_duplicate_id():
    r = BenchmarkRegistry()
    r.register(Benchmark("B1", "suite-a", "unit"))
    try:
        r.register(Benchmark("B1", "suite-b", "unit"))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_registry_rejects_empty_id():
    r = BenchmarkRegistry()
    try:
        r.register(Benchmark("", "suite-a", "unit"))
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_registry_rejects_non_benchmark():
    r = BenchmarkRegistry()
    try:
        r.register("not-a-benchmark")
        assert False, "expected EvaluationError"
    except EvaluationError:
        pass


def test_registry_deterministic_report_id():
    r = BenchmarkRegistry()
    a = r.register(Benchmark("B1", "suite-a", "unit"))
    b = BenchmarkRegistry().register(Benchmark("B1", "suite-a", "unit"))
    assert a.report_id == b.report_id
