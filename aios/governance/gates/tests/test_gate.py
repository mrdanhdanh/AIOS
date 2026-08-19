import sys, pathlib, os, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.task_registry import TaskRegistry
from aios.governance.dependency import DependencyGraph
from aios.governance.lifecycle import TaskStateMachine
from aios.governance.evidence import Evidence, EvidenceStore
from aios.governance.regression import RegressionRunner
from aios.governance.gates import TaskGate


def _full_folder():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "implementation"))
    with open(os.path.join(d, "implementation", "impl.py"), "w", encoding="utf-8") as f:
        f.write("# real code\n")
    for art in ["spec.md", "critique-1.md", "critique-2.md", "tasks.md", "review.md",
                "test.md", "evaluation.md", "EVIDENCE.md", "REGRESSION.md", "STATUS.md"]:
        with open(os.path.join(d, art), "w", encoding="utf-8") as f:
            f.write("# required\n")
    return d


def _ctx():
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Gov")
    reg.create_task("TASK-002", "Next", dependencies=["TASK-001"])
    graph = DependencyGraph(reg)
    ev = EvidenceStore()
    ev.add(Evidence("EVD-1", "TASK-002", "RUN-1", "harness", "test", "pytest",
                    "sha256:abc123", "PASS", parent_artifact="a1", environment="win"))
    regr = RegressionRunner(graph, run_test=lambda t: True)
    lc = TaskStateMachine("DONE")
    return reg, graph, ev, regr, lc


def test_gate_pass():
    reg, graph, ev, regr, lc = _ctx()
    gate = TaskGate(reg, graph, ev, regr, lc)
    r = gate.evaluate("TASK-002",
                      statuses={"TASK-001": "PASS", "TASK-002": "PASS"},
                      task_folder=_full_folder(),
                      dependency_tests_pass=True)
    assert r.passed is True
    assert r.decision() == "DONE"


def test_gate_blocked_on_missing_dependency():
    reg, graph, ev, regr, lc = _ctx()
    gate = TaskGate(reg, graph, ev, regr, lc)
    r = gate.evaluate("TASK-002",
                      statuses={"TASK-001": "PLANNED", "TASK-002": "PASS"},
                      task_folder=_full_folder(),
                      dependency_tests_pass=True)
    assert r.passed is False
    assert r.decision() == "BLOCKED"


def test_gate_blocked_on_regression_failure():
    reg, graph, ev, regr, lc = _ctx()
    gate = TaskGate(reg, graph, ev, regr, lc)
    r = gate.evaluate("TASK-002",
                      statuses={"TASK-001": "PASS", "TASK-002": "PASS"},
                      task_folder=_full_folder(),
                      dependency_tests_pass=False)
    assert r.passed is False


def test_gate_blocked_on_architecture_violation():
    reg, graph, ev, regr, lc = _ctx()
    d = _full_folder()
    with open(os.path.join(d, "implementation", "bad.py"), "w", encoding="utf-8") as f:
        f.write("import subprocess\n")
    gate = TaskGate(reg, graph, ev, regr, lc)
    r = gate.evaluate("TASK-002",
                      statuses={"TASK-001": "PASS", "TASK-002": "PASS"},
                      task_folder=d,
                      dependency_tests_pass=True)
    assert r.passed is False
