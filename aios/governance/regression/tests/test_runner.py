import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.task_registry import TaskRegistry
from aios.governance.dependency import DependencyGraph
from aios.governance.regression import RegressionRunner


def _build():
    reg = TaskRegistry()
    reg.create_task("TASK-023", "A")
    reg.create_task("TASK-024", "B")
    reg.create_task("TASK-025", "C", dependencies=["TASK-023", "TASK-024"])
    return reg


def test_regression_passes_when_closure_ok():
    reg = _build()
    runner = RegressionRunner(DependencyGraph(reg), run_test=lambda t: True)
    passed, results = runner.evaluate("TASK-025")
    assert passed is True
    assert results == {"TASK-023": True, "TASK-024": True}


def test_regression_blocks_on_dependency_failure():
    reg = _build()
    runner = RegressionRunner(DependencyGraph(reg), run_test=lambda t: t != "TASK-024")
    passed, results = runner.evaluate("TASK-025")
    assert passed is False  # Rule 7: failure in closure -> BLOCKED
    assert results["TASK-024"] is False
