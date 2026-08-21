"""Tests for evaluation harness."""

from __future__ import annotations

from aios.harness.evaluation import EvalVerdict, EvaluationCase, EvaluationResult, EvaluationSuite, Metric


class TestEvaluationSuite:
    def test_evaluate_exact_match(self) -> None:
        suite = EvaluationSuite()
        suite.add_case(EvaluationCase(case_id="c1", expected_output="hello", actual_output="hello"))
        results = suite.evaluate()
        assert results[0].verdict == EvalVerdict.PASS

    def test_evaluate_mismatch(self) -> None:
        suite = EvaluationSuite()
        suite.add_case(EvaluationCase(case_id="c1", expected_output="hello", actual_output="world"))
        results = suite.evaluate()
        assert results[0].verdict == EvalVerdict.FAIL

    def test_evaluate_empty_output_inconclusive(self) -> None:
        """AC-032-05: Missing evidence → INCONCLUSIVE."""
        suite = EvaluationSuite()
        suite.add_case(EvaluationCase(case_id="c1", expected_output="hello", actual_output=""))
        results = suite.evaluate()
        assert results[0].verdict == EvalVerdict.INCONCLUSIVE

    def test_custom_evaluator(self) -> None:
        suite = EvaluationSuite()
        suite.add_case(EvaluationCase(case_id="c1"))
        def custom(case: EvaluationCase) -> EvaluationResult:
            return EvaluationResult(case_id=case.case_id, verdict=EvalVerdict.WARNING)
        results = suite.evaluate(evaluator_fn=custom)
        assert results[0].verdict == EvalVerdict.WARNING
