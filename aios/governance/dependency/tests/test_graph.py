import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.task_registry import TaskRegistry
from aios.governance.dependency import DependencyGraph


def _build():
    reg = TaskRegistry()
    reg.create_task("TASK-023", "A")
    reg.create_task("TASK-024", "B")
    reg.create_task("TASK-025", "C", dependencies=["TASK-023", "TASK-024"])
    return reg


def test_is_ready_only_when_all_pass():
    reg = _build()
    g = DependencyGraph(reg)
    assert g.is_ready("TASK-025", {}) is False
    assert g.is_ready("TASK-025", {"TASK-023": "PASS", "TASK-024": "FAIL"}) is False
    assert g.is_ready("TASK-025", {"TASK-023": "PASS", "TASK-024": "PASS"}) is True


def test_detect_cycle():
    reg = TaskRegistry()
    reg.create_task("TASK-100", "x", dependencies=["TASK-101"])
    reg.create_task("TASK-101", "y", dependencies=["TASK-100"])
    g = DependencyGraph(reg)
    assert g.detect_cycle("TASK-100") is True


def test_closure():
    reg = _build()
    g = DependencyGraph(reg)
    assert g.closure("TASK-025") == {"TASK-023", "TASK-024"}
