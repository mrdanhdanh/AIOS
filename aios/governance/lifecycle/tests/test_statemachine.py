import sys, pathlib, tempfile, os
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.lifecycle import TaskStateMachine, LifecycleError, REQUIRED_FOR_DONE


def test_linear_progression():
    sm = TaskStateMachine("PLANNED")
    for nxt in ["SPECIFIED", "CRITIQUED_1", "CRITIQUED_2", "BROKEN_DOWN",
                "REVIEWED", "IMPLEMENTING", "TESTING", "EVALUATING",
                "REGRESSION", "READY_TO_CLOSE", "DONE"]:
        sm.transition(nxt)
    assert sm.state == "DONE"


def test_illegal_transition_rejected():
    sm = TaskStateMachine("PLANNED")
    try:
        sm.transition("DONE")
        assert False, "should reject skip"
    except LifecycleError:
        pass


def test_missing_artifact_blocks_done():
    d = tempfile.mkdtemp()
    ok, missing = TaskStateMachine.artifacts_present(d)
    assert ok is False
    assert set(REQUIRED_FOR_DONE).issubset(set(missing + ["implementation"]))


def test_full_artifacts_pass():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "implementation"))
    with open(os.path.join(d, "implementation", "impl.py"), "w", encoding="utf-8") as f:
        f.write("# real code\n")
    for art in REQUIRED_FOR_DONE:
        if art == "implementation":
            continue
        with open(os.path.join(d, art), "w", encoding="utf-8") as f:
            f.write("# required\n")
    ok, missing = TaskStateMachine.artifacts_present(d)
    assert ok is True and missing == []
