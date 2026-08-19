import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aios.governance.architecture import scan_source, RULES


def test_agent_subprocess_forbidden():
    code = "import subprocess\nsubprocess.run('ls')\n"
    v = scan_source(code, is_agent=True)
    assert any(x.rule_id == "ARCH-001" for x in v)


def test_agent_provider_import_forbidden():
    code = "from aios.providers.openai import call\n"
    v = scan_source(code, is_agent=True)
    assert any(x.rule_id == "ARCH-003" for x in v)


def test_clean_agent_no_violation():
    code = "from aios.runtime import Runtime\nruntime.execute()\n"
    v = scan_source(code, is_agent=True)
    assert v == []
