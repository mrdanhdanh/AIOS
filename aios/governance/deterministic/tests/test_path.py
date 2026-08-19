import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.deterministic import DeterministicControlPath, ControlPathError


def test_deterministic_no_llm():
    cp = DeterministicControlPath()
    out = cp.route(can_decide=True, planner=lambda: "should-not-run")
    assert out["used_llm"] is False
    assert cp.llm_calls == 0  # Rule 4: LLM not the default control plane


def test_llm_fallback_validated():
    cp = DeterministicControlPath()
    out = cp.route(can_decide=False, planner=lambda: "plan", validator=lambda x: x == "plan")
    assert out["used_llm"] is True
    assert cp.llm_calls == 1


def test_llm_output_must_validate():
    cp = DeterministicControlPath()
    try:
        cp.route(can_decide=False, planner=lambda: "bad", validator=lambda x: x == "plan")
        assert False, "should reject unvalidated planner output"
    except ControlPathError:
        pass
