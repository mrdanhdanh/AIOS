"""Regression Runner — Rule 7 (run dependency closure tests before PASS). Fail-closed."""
from ..dependency.graph import DependencyGraph


class RegressionRunner:
    def __init__(self, graph: DependencyGraph, run_test):
        self.graph = graph
        self.run_test = run_test  # callable(task_id) -> bool

    def evaluate(self, task_id):
        try:
            closure = self.graph.closure(task_id)
        except Exception:
            return False, {}
        results = {}
        for t in closure:
            try:
                results[t] = bool(self.run_test(t))
            except Exception:
                results[t] = False  # fail-closed: exception = BLOCKED
        passed = all(results.values()) if results else True
        return passed, results
